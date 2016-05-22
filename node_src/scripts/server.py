from bottle import *

import urllib2
import subprocess
import socket
import json
import re
import logging
import traceback
from ethoscope_node.utils.helpers import generate_new_device_map, update_dev_map_wrapped, get_local_ip, get_internet_ip
from ethoscope_node.utils.helpers import get_last_backup_time
import shutil
import tempfile

from os import walk
import optparse
import zipfile
import datetime
import fnmatch
from netifaces import ifaddresses, AF_INET, AF_LINK



app = Bottle()
STATIC_DIR = "../static"


def update_device_map(id, what="data",type=None, port=9000, data=None):
    global  devices_map
    update_dev_map_wrapped(LOCAL_IP, devices_map,id,what,type,port,data,result_main_dir=RESULTS_DIR )


@app.get('/favicon.ico')
def get_favicon():
    return server_static(STATIC_DIR+'/img/favicon.ico')

@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=STATIC_DIR)

@app.route('/tmp_static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=tmp_imgs_dir)

@app.route('/download/<filepath:path>')
def server_download(filepath):
    return static_file(filepath, root="/", download=filepath)

@app.route('/')
def index():
    return static_file('index.html', root=STATIC_DIR)


@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8888'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


#################################
# API to connect with SM/SD
#################################



@app.get('/devices')
def scan_subnet( ip_range=(6,100)):
    global devices_map
    try:
        devices_map_tmp = generate_new_device_map(LOCAL_IP, ip_range)
        detected_devices = devices_map_tmp.keys()
        for k in detected_devices:
            if k in devices_map:
                devices_map[k].update(devices_map_tmp[k])
            else:
                logging.info("new device detected %s" % k)
                devices_map[k] = devices_map_tmp[k]



        for k in devices_map.keys():
             if k not in detected_devices:
                 logging.warning("Device %s not detected when scanning" % k)
                 devices_map[k]["status"] = "not detected"

        return devices_map

    
    except Exception as e:
        logging.error("Unexpected exception whilst scanning devices:")
        logging.error(traceback.format_exc(e))


@app.get('/devices_list')
def get_devices_list():
    global devices_map
    return devices_map


#Get the information of one Sleep Monitor
@app.get('/device/<id>/data')
def device(id):
    try:
        update_device_map(id,what="data")
        return devices_map[id]
    except Exception as e:
        return {'error':traceback.format_exc(e)}

#Get the information of one Sleep Monitor
@app.get('/device/<id>/user_options')
def device(id):
    try:

        device_info = devices_map[id]
        dev_ip = device_info["ip"]

        url = dev_ip +':9000/user_options/' + id
        out = urllib2.urlopen(url)

        return out

    except Exception as e:
        return {'error':traceback.format_exc(e)}




#Get the information of one Sleep Monitor
@app.get('/device/<id>/last_img')
def device(id):
    try:
        device_info = devices_map[id]
        dev_ip = device_info["ip"]
        img_path = device_info["last_drawn_img"]
        url = dev_ip +':9000/static' + img_path
        file_like = urllib2.urlopen(url)
        # Open our local file for writing
        local_file = os.path.join(tmp_imgs_dir, id + ".jpg")
        with open(local_file, "wb") as lf:
            lf.write(file_like.read())
        return os.path.basename(local_file)

    except Exception as e:
        return {'error':traceback.format_exc(e)}


@app.post('/device/<id>/controls/<type_of_req>')
def device(id, type_of_req):
    try:
        post_data = request.body.read()
        update_device_map(id, "data")
        device_info = devices_map[id]

        if type_of_req == 'start':
            if device_info['status'] == 'stopped':
                update_device_map(id, "controls", type_of_req, data=post_data)
            else:
                raise Exception("Cannot start, device %s status is `%s`" %  (id, device_info['status']))

        elif type_of_req == 'stop':

            if device_info['status'] == 'running' or device_info['status'] == 'recording':
                stop_device(id,post_data)
            else:
                raise Exception("Cannot stop, device %s status is `%s`" %  (id, device_info['status']))
        elif type_of_req == 'start_record':
            if device_info['status'] == 'stopped':
                update_device_map(id, 'controls', type_of_req, data=post_data)
            else:
                raise Exception("Cannot %s recording, device %s status is %s"% (type_of_req, id, device_info['status']))
        elif type_of_req == 'stop_record':
            if device_info['status'] == 'recording':
                update_device_map(id, 'controls', type_of_req, data=post_data)
            else:
                raise Exception("Cannot %s recording, device %s status is %s"% (type_of_req, id, device_info['status']))

        elif type_of_req == 'poweroff':
            if device_info['status'] == 'running':
                stop_device(id, post_data)
            update_device_map(id, "controls", type_of_req, data=post_data)

    except Exception as e:
        logging.error(traceback.format_exc(e))
        return {'error':traceback.format_exc(e)}

def stop_device(id, post_data):
    update_device_map(id, "controls", 'stop', data=post_data)

@app.post('/device/<id>/log')
def get_log(id):
    try:

        data = request.body.read()
        data = json.loads(data)

        #TO DISCUSS @luis static files url not understood
        req = urllib2.Request(url=devices_map[id]['ip']+':9000/static'+data["file_path"])

        f = urllib2.urlopen(req)
        result = {}
        for i, line in enumerate(f):
            result[i]=line

        return result

    except Exception as e:
        return {'error':traceback.format_exc(e)}

#################################
# NODE Functions
#################################


#Browse, delete and download files from node

@app.get('/result_files/<type>')
def result_file(type):
    """
    :param type:'all', 'db' or 'txt'
    :return: a dict with a single key: "files" which maps a list of matching result files (absolute path)
    """

    try:
        type="txt"
        if type == "all":
            pattern =  '*'
        else:
            pattern =  '*.'+type

        matches = []
        for root, dirnames, filenames in os.walk(RESULTS_DIR):
            for f in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, f))
            return {"files":matches}

    except Exception as e:
        logging.error(traceback.format_exc(e))
        return {'error':traceback.format_exc(e)}


@app.get('/browse/<folder:path>')
def browse(folder):
    try:
        if folder == 'null':
            directory = RESULTS_DIR
        else:
            directory = '/'+folder
        files = []
        for (dirpath, dirnames, filenames) in walk(directory):
            for name in filenames:
                abs_path = os.path.join(dirpath,name)
                size = os.path.getsize(abs_path)
                #rel_path = os.path.relpath(abs_path,directory)
                files.append({'abs_path':abs_path, 'size':size})

        return {'files': files}

    except Exception as e:
        return {'error': traceback.format_exc(e)}




@app.post('/request_download/<what>')
def download(what):
    try:
        # zip the files and provide a link to download it
        if what == 'files':
            req_files = request.json
            t = datetime.datetime.now()
            #FIXME change the route for this? and old zips need to be erased
            zip_file_name = os.path.join(RESULTS_DIR,'results_'+t.strftime("%y%m%d_%H%M%S")+'.zip')
            zf = zipfile.ZipFile(zip_file_name, mode='a')
            logging.info("Saving files : %s in %s" % (str(req_files['files']), zip_file_name) )
            for f in req_files['files']:
                zf.write(f['url'])
            zf.close()

            return {'url':zip_file_name}

        else:
            raise NotImplementedError()

    except Exception as e:
        logging.error(e)
        return {'error': traceback.format_exc(e)}

@app.get('/node/<req>')
def node_info(req):#, device):
    try:
        if req == 'info':
            df = subprocess.Popen(['df', RESULTS_DIR, '-h'], stdout=subprocess.PIPE)
            disk_free = df.communicate()[0]
            disk_usage = RESULTS_DIR+" Not Found on disk"
            # ip = "No IP assigned, check cable"
            # MAC_addr = "Not detected"
            # local_ip = ""
            # try:
            #     disk_usage = disk_free.split("\n")[1].split()
            #     addrs = ifaddresses(INTERNET_DEVICE)
            #     MAC_addr = addrs[AF_LINK][0]["addr"]
            #
            #     ip = addrs[AF_INET][0]["addr"]
            #     local_addrs = ifaddresses(SUBNET_DEVICE)
            #     local_ip = local_addrs[AF_INET][0]["addr"]
            # except Exception as e:
            #     logging.error(e)
            #fixme
            MAC_addr = "TODO"
            return {'disk_usage': disk_usage, 'MAC_addr': MAC_addr, 'ip': WWW_IP,
                    'local_ip':LOCAL_IP}
        if req == 'time':
            return {'time':datetime.datetime.now().isoformat()}
        else:
            raise NotImplementedError()
    except Exception as e:
        logging.error(e)
        return {'error': traceback.format_exc(e)}

@app.post('/node-actions')
def node_actions():
    try:
        action = request.json
        if action['action'] == 'poweroff':
            logging.info('User request a poweroff, shutting down system. Bye bye.')

            close()
            #poweroff = subprocess.Popen(['poweroff'], stdout=subprocess.PIPE)
        elif action['action'] == 'close':
            close()
        else:
            raise NotImplementedError()
    except Exception as e:
        logging.error(e)
        return {'error': traceback.format_exc(e)}

@app.post('/remove_files')
def remove_files():
    try:
        req = request.json
        res = []
        for f in req['files']:
            rm = subprocess.Popen(['rm', f['url']],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
            out, err = rm.communicate()
            logging.info(out)
            logging.error(err)
            res.append(f['url'])
        return {'result': res}
    except Exception as e:
        logging.error(e)
        return {'error': traceback.format_exc(e)}


@app.get('/list/<type>')
def redirection_to_home(type):
    return redirect('/#/list/'+type)
@app.get('/more')
def redirection_to_home():
    return redirect('/#/more/')
@app.get('/ethoscope/<id>')
def redirection_to_home(id):
    return redirect('/#/ethoscope/'+id)
@app.get('/device/<id>/ip')
def redirection_to_home(id):
    if len(devices_map) > 0:
        return devices_map[id]['ip']
    else:
        return "no devices"
@app.get('/more/<action>')
def redirection_to_more(action):
    return redirect('/#/more/'+action)

def close(exit_status=0):
    logging.info("Closing server")
    os._exit(exit_status)
    

#======================================================================================================================#

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    parser = optparse.OptionParser()
    parser.add_option("-D", "--debug", dest="debug", default=False,help="Set DEBUG mode ON", action="store_true")
    parser.add_option("-p", "--port", dest="port", default=80,help="port")
    parser.add_option("-l", "--local", dest="local", default=False, help="Run on localhost (run a node and device on the same machine, for development)", action="store_true")
    parser.add_option("-e", "--results-dir", dest="results_dir", default="/ethoscope_results",help="Where temporary result files are stored")
    parser.add_option("-r", "--router-ip", dest="router_ip", default="192.169.123.254", help="the ip of the router in your setup")



    (options, args) = parser.parse_args()

    option_dict = vars(options)
    PORT = option_dict["port"]
    DEBUG = option_dict["debug"]
    RESULTS_DIR = option_dict["results_dir"]
    if option_dict["local"]:
        LOCAL_IP  = "127.0.0.1"
    else:
        LOCAL_IP = get_local_ip(option_dict["router_ip"])

    try:
        WWW_IP = get_internet_ip()
    except Exception as e:
        logging.warning("Could not access internet!")
        logging.warning(traceback.format_exc(e))
        WWW_IP = None

    global devices_map
    devices_map = {}
    scan_subnet()


    tmp_imgs_dir = tempfile.mkdtemp(prefix="ethoscope_node_imgs")
    try:
        run(app, host='0.0.0.0', port=PORT, debug=DEBUG, server='cherrypy')

    except KeyboardInterrupt:
        logging.info("Stopping server cleanly")
        pass

    except socket.error as e:
        logging.error(traceback.format_exc(e))
        logging.error("Port %i is probably not accessible for you. Maybe use another one e.g.`-p 8000`" % PORT)

    except Exception as e:
        logging.error(traceback.format_exc(e))
        close(1)
    finally:
        shutil.rmtree(tmp_imgs_dir)
        close()
