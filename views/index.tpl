<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="stylesheet" href="static/css/bootstrap.min.css">
        <style>
            body {
                padding-top: 50px;
                padding-bottom: 20px;
            }
        </style>
        <link rel="stylesheet" href="static/css/bootstrap-theme.min.css">
        <link rel="stylesheet" href="static/css/main.css">

        <script src="static/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js"></script>
    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="browsehappy">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> to improve your experience.</p>
        <![endif]-->
    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">PySolo ControlPanel:{{machineId}}</a>
            
        </div>
        <div class="navbar-collapse collapse">
          <form class="navbar-form navbar-right" role="form">
            <div class="form-group">
              <input type="text" placeholder="Email" class="form-control">
            </div>
            <div class="form-group">
              <input type="password" placeholder="Password" class="form-control">
            </div>
            <button type="submit" class="btn btn-success">Sign in</button>
          </form>
        </div><!--/.navbar-collapse -->
      </div>
    </div>

    <!-- Main jumbotron for a primary marketing message or call to action -->
    <div class="jumbotron">
      <div class="container text-center">
        <div class="row">
        <h2>PySolo-Video Browser editor</h2>
          <div id="ROI-input" class="col-md-12">
            <canvas id="ROIView" width="500" height="300"></canvas>
              <!--<canvas id="drawingCanvas" width="500" height="300"></canvas>-->
         </div>
          </div>
          <div class="row ">
                <div class=" col-md-12">
                    <div class="btn-group">
                        <button type="button" id="removeLast" class="btn btn-default" href="#" role="button">Remove last</button>
                        <button type="button" id="autoMask"class="btn btn-default" href="#" role="button">Auto mask</button>
                        </div>
                    <div class="btn-group">
                        <button type="button" id="saveRoi" class="btn btn-default" href="#" role="button">Save</button>
                        <button type="button" id="loadRoi"class="btn btn-default" href="#" role="button">Load</button>
                    </div>
                </div>
            
            <div class="row text-center">
                <div id="pickloaded" class="col-md-12">
                    
                </div>
            </div>
       </div>
      </div>
    </div>

    <div class="container">
      <!-- Example row of columns -->
      <div class="row">
        <div class="col-md-4">
          <h2>Refresh</h2>
          <p>Click Here to refresh the camera image</p>
          <p><button type="button" id="refreshBackground"class="btn btn-default" href="#" role="button">Refresh</button></p>
        </div>
%if status == True:
          <div class="col-md-4">
            <h2>Tracking ongoing</h2>
            <p>Tracking is already ongoing</p>
              <p><button type="button" id="start" class=" btn btn-success" href="#" role="button" disabled>Start</button></p>
         </div>
        <div class="col-md-4">
          <h2>Stop Tracking</h2>
          <p>Stops the tracking system.</p>
          <p><button type="button" id="stop" class="btn btn-danger" href="#" role="button">Stop</button></p>
        </div>
%else:
        <div class="col-md-4">
          <h2>Start Tracking</h2>
          <p>Select tracking type</p>
             <form class="">
              <div class="track-select">
                <div class="input-group"><label>
                    <input type="radio" name="optionTrack" id="optionTrack0" value="0">
                    Position</label>
                    
                </div>
                <div class="input-group ">
                    <input type="radio" name="optionTrack" id="optionTrack1" value="1">
                    <label>Distance</label>
                </div>
                <div class="input-group">
                    <input type="radio" name="optionTrack" id="optionTrack2" value="2">
                    <label>XY Coordinates</label>
                </div>
              </div>
            <p><button type="submit" id="start" class=" btn btn-success" href="#" role="button" >Start</button></p>
              </form>
        </div>
        <div class="col-md-4">
              <h2>Stop Tracking</h2>
              <p>Stops the tracking system.</p>
              <p><button type="button" id="stop" class="btn btn-danger" href="#" role="button" disabled>Stop</button></p>
         </div>
%end
       </div>
      </div>

      <hr>

      <footer>
        <p>&copy; Polygonal Tree 2014</p>
      </footer>
    </div> <!-- /container -->        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script src="static/js/vendor/jquery-1.11.0.min.js"><\/script>')</script>

        <script src="static/js/vendor/bootstrap.min.js"></script>

        <script src="static/js/main.js"></script>
    </body>
</html>

