from pymodaq_utils.enums import BaseEnum, enum_checker

import cv2


class OpenCVProp(BaseEnum):
    # modes of the controlling registers (can be: auto, manual, auto single push, absolute Latter allowed with any other mode)
    # every feature can have only one mode turned on at a time
    CV_CAP_PROP_DC1394_OFF = -4  # turn the feature off (not controlled manually nor automatically)
    CV_CAP_PROP_DC1394_MODE_MANUAL = -3  # set automatically when a value of the feature is set by the user
    CV_CAP_PROP_DC1394_MODE_AUTO = -2
    CV_CAP_PROP_DC1394_MODE_ONE_PUSH_AUTO = -1
    CV_CAP_PROP_POS_MSEC = 0
    CV_CAP_PROP_POS_FRAMES = 1
    CV_CAP_PROP_POS_AVI_RATIO = 2
    CV_CAP_PROP_FRAME_WIDTH = 3
    CV_CAP_PROP_FRAME_HEIGHT = 4
    CV_CAP_PROP_FPS = 5
    CV_CAP_PROP_FOURCC = 6
    CV_CAP_PROP_FRAME_COUNT = 7
    CV_CAP_PROP_FORMAT = 8
    CV_CAP_PROP_MODE = 9
    CV_CAP_PROP_BRIGHTNESS = 10
    CV_CAP_PROP_CONTRAST = 11
    CV_CAP_PROP_SATURATION = 12
    CV_CAP_PROP_HUE = 13
    CV_CAP_PROP_GAIN = 14
    CV_CAP_PROP_EXPOSURE = 15
    CV_CAP_PROP_CONVERT_RGB = 16
    CV_CAP_PROP_WHITE_BALANCE_BLUE_U = 17
    CV_CAP_PROP_RECTIFICATION = 18
    CV_CAP_PROP_MONOCHROME = 19
    CV_CAP_PROP_SHARPNESS = 20
    CV_CAP_PROP_AUTO_EXPOSURE = 21  # exposure control done by camera
    # user can adjust reference level
    # using this feature
    CV_CAP_PROP_GAMMA = 22
    CV_CAP_PROP_TEMPERATURE = 23
    CV_CAP_PROP_TRIGGER = 24
    CV_CAP_PROP_TRIGGER_DELAY = 25
    CV_CAP_PROP_WHITE_BALANCE_RED_V = 26
    CV_CAP_PROP_ZOOM = 27
    CV_CAP_PROP_FOCUS = 28
    CV_CAP_PROP_GUID = 29
    CV_CAP_PROP_ISO_SPEED = 30
    CV_CAP_PROP_MAX_DC1394 = 31
    CV_CAP_PROP_BACKLIGHT = 32
    CV_CAP_PROP_PAN = 33
    CV_CAP_PROP_TILT = 34
    CV_CAP_PROP_ROLL = 35
    CV_CAP_PROP_IRIS = 36
    CV_CAP_PROP_SETTINGS = 37
    CV_CAP_PROP_BUFFERSIZE = 38
    CV_CAP_PROP_AUTOFOCUS = 39
    CV_CAP_PROP_SAR_NUM = 40
    CV_CAP_PROP_SAR_DEN = 41


