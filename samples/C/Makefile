SHELL := /bin/bash
OS := $(shell uname)

ifeq ($(OS), Darwin)
  LDLIBS := ../../lib/libLeapC.dylib -lpthread
  GLUT_LIBS := -framework GLUT -framework OpenGL
  CC := gcc
  CFLAGS := -Wall -Wno-deprecated -g
  HOST_TOOLCHAIN := darwin-x86_64
else ifeq ($(OS), Linux)
  LDLIBS := ../../lib/libLeapC.so -lpthread
  GLUT_LIBS := -lGL -lGLU -lglut
  CC := gcc
  CFLAGS := -Wall -Wno-deprecated -g -std=gnu99
  HOST_TOOLCHAIN := linux-x86_64
else ifneq ($(findstring MINGW, $(OS)),)
  HOST_TOOLCHAIN := windows
else ifneq ($(findstring CYGWIN, $(OS)),)
  HOST_TOOLCHAIN := windows
endif

ifdef BUILD_ANDROID
  ifeq ($(TARGET_ARCH), arm64)
    TARGET_TOOLCHAIN := aarch64-linux-android
  else
    TARGET_TOOLCHAIN := arm-linux-androideabi
  endif
  # please change this to point to your NDK location
  ifndef NDK
    ifneq ($(MAKECMDGOALS), clean)
      $(error NDK variable must be set to build for Android)
    endif
  endif
  SYSROOT := $(NDK)/platforms/android-21/arch-$(TARGET_ARCH)
  ifneq ("$(wildcard $(NDK)/toolchains/$(TARGET_TOOLCHAIN)-4.9/prebuilt/$(HOST_TOOLCHAIN)-x86_64)", "")
    HOST_TOOLCHAIN := $(HOST_TOOLCHAIN)-x86_64
  endif
  CC := $(NDK)/toolchains/$(TARGET_TOOLCHAIN)-4.9/prebuilt/$(HOST_TOOLCHAIN)/bin/$(TARGET_TOOLCHAIN)-gcc-4.9 --sysroot=$(SYSROOT)
  CFLAGS += -fPIE -std=c99
  LDLIBS := ../../lib/libLeapC.so -pthread -lm -fPIE -pie
endif

all: CallbackSample ImageSample InterpolationSample PollingSample

%.o: %.c ExampleConnection.h ../../include/LeapC.h
	$(CC) -c $(CFLAGS) -I../../include $< -o $@

CallbackSample: CallbackSample.o ExampleConnection.o
	$(CC) $^ -o $@ $(LDLIBS)
	$(call install_lib,$@)

ImageSample: ImageSample.o ExampleConnection.o
	$(CC) $^ -o $@ $(LDLIBS)
	$(call install_lib,$@)

InterpolationSample: InterpolationSample.o ExampleConnection.o
	$(CC) $^ -o $@ $(LDLIBS)
	$(call install_lib,$@)

PollingSample: PollingSample.o ExampleConnection.o
	$(CC) $^ -o $@ $(LDLIBS)
	$(call install_lib,$@)

ifndef BUILD_ANDROID
GLUTImageSample: GLUTImageSample.o ExampleConnection.o GLutils.o
	$(CC) $^ -o $@ $(LDLIBS) $(GLUT_LIBS)
	$(call install_lib,$@)

GLUTSample: GLUTSample.o ExampleConnection.o GLutils.o
	$(CC) -o $@ $(LDLIBS) $(GLUT_LIBS)
	$(call install_lib,$@)

all: GLUTImageSample GLUTSample
endif

install_lib =
ifndef BUILD_ANDROID
  ifeq ($(OS), Darwin)
    install_lib = \
      install_name_tool -change @loader_path/libLeapC.dylib ../../lib/libLeapC.dylib $(1);
  endif
endif

clean:
	rm -rf *.o *Sample *Sample.dSYM
