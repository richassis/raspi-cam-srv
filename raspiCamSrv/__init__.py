import os
from pathlib import Path
from flask import Flask, g
import logging
from flask.logging import default_handler
from picamera2 import Picamera2
from raspiCamSrv.camera_pi import Camera
from raspiCamSrv.motionDetector import MotionDetector
import json
import datetime
import time
from werkzeug.serving import is_running_from_reloader
import threading
from .home import take_raw_photo  # Importa a função take_raw_photo

def start_timelapse(logger):
    logTime = str(datetime.datetime.now())
    logger.debug(logTime + ": Iniciando timelapse")
    # Cria um contexto de aplicação
    with app.app_context():
        # Define um usuário simulado
        g.user = {'id': 1, 'username': 'stihl', 'issuperuser': 1, 'isinitial': 0}
        # Cria um contexto de requisição
        with app.test_request_context('/take_raw_photo', method='POST'):
            # Chama a função take_raw_photo
            logger.debug(logTime + ": Executando take_raw_photo")
            take_raw_photo()
            logger.debug(logTime + ": Função take_raw_photo executada com sucesso")

def timelapse_thread():

    logger = logging.getLogger("pc2_prg")
    logPath = os.path.dirname(app.instance_path) + "/logs"
    logFilename = "timelapse.log"
    logFile = logPath+ "/" + logFilename
    #>>>>> Uncomment the following 5 lines when code generation is activated (see below)
    Path(logFile).touch(exist_ok=True)
    fileHandler = logging.FileHandler(logFile)
    formatter = logging.Formatter('%(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

    # Adiciona um atraso de 1 minuto
    time.sleep(60)
    while True:
        logTime = str(datetime.datetime.now())
        logger.debug(logTime + ": Executando start_timelapse")
        start_timelapse(logger)
        logger.debug(logTime + ": Função start_timelapse executada com sucesso")
        time.sleep(1800)  # 1800 seconds = 30 minutes

def create_app(test_config=None):
    global app  # Torna a variável app global para ser usada em start_timelapse
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "raspiCamSrv.sqlite"),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configure loggers
    logsPath = os.path.dirname(app.instance_path) + "/logs"
    os.makedirs(logsPath, exist_ok=True)
    logFile = logsPath + "/raspiCamSrv.log"
    Path(logFile).touch(exist_ok=True)
    filehandler = logging.FileHandler(logFile)
    filehandler.setFormatter(app.logger.handlers[0].formatter)

    for logger in(
        app.logger,
        logging.getLogger("werkzeug"),
        logging.getLogger("raspiCamSrv.db"),
        logging.getLogger("raspiCamSrv.auth"),
        logging.getLogger("raspiCamSrv.auth_su"),
        logging.getLogger("raspiCamSrv.camCfg"),
        logging.getLogger("raspiCamSrv.camera_pi"),
        logging.getLogger("raspiCamSrv.config"),
        logging.getLogger("raspiCamSrv.home"),
        logging.getLogger("raspiCamSrv.images"),
        logging.getLogger("raspiCamSrv.info"),
        logging.getLogger("raspiCamSrv.settings"),
        logging.getLogger("raspiCamSrv.photoseries"),
        logging.getLogger("raspiCamSrv.photoseriesCfg"),
        logging.getLogger("raspiCamSrv.trigger"),
        logging.getLogger("raspiCamSrv.motionDetector"),
        logging.getLogger("raspiCamSrv.motionAlgoIB"),
        logging.getLogger("raspiCamSrv.webcam"),
        logging.getLogger("raspiCamSrv.sun"),
        logging.getLogger("raspiCamSrv.api"),
    ):
        logger.setLevel(logging.ERROR)

    #>>>>> Uncomment the following line in order to log to the log file
    #app.logger.addHandler(filehandler)

    #>>>>> Explicitely set specific log levels. Leave "werkzeug" at INFO
    logging.getLogger("werkzeug").setLevel(logging.INFO)
    #logging.getLogger("raspiCamSrv.auth").setLevel(logging.ERROR)
    #logging.getLogger("raspiCamSrv.camCfg").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.camera_pi").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.images").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.webcam").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.trigger").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.photoseriesCfg").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.photoseries").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.sun").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.motionDetector").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.motionAlgoIB").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.settings").setLevel(logging.DEBUG)
    #logging.getLogger("raspiCamSrv.api").setLevel(logging.DEBUG)
    
    #>>>>> Set log level for picamera2 (DEBUG, INFO, WARNING, ERROR)
    Picamera2.set_logging(Picamera2.ERROR)
    #>>>>> Uncomment the following line to let Picamera2 log to the log file
    #logging.getLogger("picamera2").addHandler(filehandler)
        
    #>>>>> Set log level for libcamera (0:DEBUG, 1:INFO, 2:WARNING, 3:ERROR, 4:FATAL)
    os.environ["LIBCAMERA_LOG_LEVELS"] = "*:3"

    #Configure the logger for generation of program code
    #This logger generates an executable Picamera2 Python application program
    #including the entire interaction with Picamera2 during a server run
    prgOutPath = os.path.dirname(app.instance_path) + "/output"
    os.makedirs(prgOutPath, exist_ok=True)
    prgLogger = logging.getLogger("pc2_prg")
    prgLogPath = os.path.dirname(app.instance_path) + "/logs"
    prgLogTime = datetime.datetime.now()
    prgLogFilename = "prgLog_" + prgLogTime.strftime("%Y%m%d_%H%M%S") + ".log"
    prgLogFile = prgLogPath+ "/" + prgLogFilename
    #>>>>> Uncomment the following 5 lines when code generation is activated (see below)
    Path(prgLogFile).touch(exist_ok=True)
    prgFilehandler = logging.FileHandler(prgLogFile)
    prgFormatter = logging.Formatter('%(message)s')
    prgFilehandler.setFormatter(prgFormatter)
    prgLogger.addHandler(prgFilehandler)
    #>>>>> To activate Python code generation, set level to DEBUG
    #prgLogger.setLevel(logging.DEBUG)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Make database available in the application context
    from . import db
    db.init_app(app)
    
    # Configure Config
    from . import camCfg
    from . import settings
    cfg = camCfg.CameraCfg()
    sc = cfg.serverConfig
    sc.photoRoot = app.static_folder
    sc.prgOutputPath = prgOutPath
    sc.checkEnvironment()
    if sc.supportsExtMotionDetection == False:
        cfg.triggerConfig.motionDetectAlgos = ["Mean Square Diff",]
    cfgPath = app.static_folder + "/config"
    if settings.getLoadConfigOnStart(cfgPath):
        cfg.loadConfig(cfgPath)
    cfg = camCfg.CameraCfg()
    sc = cfg.serverConfig
    sc.checkEnvironment()
    sc.database = os.path.join(app.instance_path, "raspiCamSrv.sqlite")
        
    # Configure Triggered Capture        
    tcActionPath = app.static_folder + "/events"
    os.makedirs(tcActionPath, exist_ok=True)
    tc = cfg.triggerConfig
    tc.actionPath = tcActionPath
    Path(tc.logFilePath).touch(exist_ok=True)
        
    # Configure Photoseries
    from . import photoseriesCfg
    tlRootPath = app.static_folder + "/photoseries"
    os.makedirs(tlRootPath, exist_ok=True)
    tlCfg = photoseriesCfg.PhotoSeriesCfg()
    tlCfg.rootPath = tlRootPath
    tlCfg.initFromTlFolder()
    tlCfg = photoseriesCfg.PhotoSeriesCfg()
    
    # Restart an active series if requested
    if tlCfg.hasCurSeries:
        sr = tlCfg.curSeries
        if sr.status == "ACTIVE":
            if sr.isExposureSeries == False \
            and sr.isFocusStackingSeries == False:
                if sr.continueOnServerStart == True:
                    sr.nextStatus("pause")
                    # Start live stream in order to load lowres config for later live stream compatibility
                    Camera().startLiveStream()
                    Camera().startPhotoSeries(sr)
                    time.sleep(2)
                    if sc.error is None and sr.error is None:
                        sr.nextStatus("start")
                else:
                    sr.nextStatus("pause")
            else:
                sr.nextStatus("pause")

    # Autostart triggered capture, if configured
    if tc.operationAutoStart:
        MotionDetector().startMotionDetection()
        sc.isTriggerRecording = True
    
    # Register required blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import home
    app.register_blueprint(home.bp)
    app.add_url_rule("/", endpoint="index")

    from . import config
    app.register_blueprint(config.bp)

    from . import images
    app.register_blueprint(images.bp)

    from . import info
    app.register_blueprint(info.bp)

    from . import settings
    app.register_blueprint(settings.bp)

    from . import photoseries
    app.register_blueprint(photoseries.bp)

    from . import trigger
    app.register_blueprint(trigger.bp)

    from . import webcam
    app.register_blueprint(webcam.bp)

    if sc.useAPI == True:
        from . import api
        app.register_blueprint(api.bp)

        from flask_jwt_extended import JWTManager    
        
        if sc.jwtAuthenticationActive == False:
            sc.API_active = False
        else:
            sc.API_active = True
            app.config["JWT_SECRET_KEY"] = cfg.secrets.jwtSecretKey
            if sc.jwtAccessTokenExpirationMin > 0:
                app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(minutes=sc.jwtAccessTokenExpirationMin)
            if sc.jwtRefreshTokenExpirationDays > 0:
                app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=sc.jwtRefreshTokenExpirationDays)
            jwt = JWTManager(app)

    # Start the timelapse thread
    timelapse_thread_instance = threading.Thread(target=timelapse_thread)
    timelapse_thread_instance.daemon = True
    timelapse_thread_instance.start()

    return app
