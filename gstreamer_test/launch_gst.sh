# see https://docs.exploredeepwater.com/guides/pi_setup.html for the original streaming command
#gst-launch-1.0 -v v4l2src device=/dev/video1 ! video/x-h264, width=1920,height=1080! h264parse ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.82 port=5600 sync=false
# using a non-h264 cheap-ass USB camera meant I had to modify the command to run raw video
# Apparently the cheapo camera doesn't like doing 1920x1080 raw 
#RESOLUTION="width=640,height=480"
RESOLUTION="width=1280,height=720"
#RESOLUTION="width=1920,height=1080"
FRAMERATE="framerate=30/1"
FRAMERATE="framerate=15/1"
#gst-launch-1.0 -v v4l2src device=/dev/video0 ! 'video/x-raw,width=640,height=480,framerate=30/1' ! videoconvert ! omxh264enc ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.82 port=5600 sync=false
gst-launch-1.0 -v v4l2src device=/dev/video0 ! "video/x-raw,${RESOLUTION},${FRAMERATE}" ! videoconvert ! omxh264enc ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.82 port=5600 sync=false
#gst-launch-1.0 -v v4l2src device=/dev/video0 ! 'video/x-raw,width=1920,height=1080,framerate=30/1' ! videoconvert ! omxh264enc ! queue ! rtph264pay config-interval=10 pt=96 ! udpsink host=192.168.1.82 port=5600 sync=false

