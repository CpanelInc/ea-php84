OBS_PROJECT := EA4
OBS_PACKAGE := ea-php84
DISABLE_BUILD := repository=CentOS_6.5_standard repository=CentOS_7 repository=xUbuntu_20.04
include $(EATOOLS_BUILD_DIR)obs.mk
