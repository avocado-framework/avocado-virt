# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.
#
# Copyright (C) 2014 Red Hat Inc

"""
Encoder transforms screenshots taken during a test into a HTML 5
compatible video, so that one can watch the screen activity of the
whole test from inside your own browser.

This relies on generally available multimedia libraries, frameworks
and tools. This code was inspired on virt-test, ported to the more recent
gobject introspection API.

Author: Cleber Rosa <crosa@redhat.com>
Author: Lucas Meneghel Rodrigues <lmr@redhat.com>
"""

import glob
import os
import re
import logging
from PIL import Image

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

from avocado.virt import defaults

log = logging.getLogger("avocado.test")


class EncodingError(Exception):

    def __init__(self, err, debug):
        self.err = err
        self.debug = debug

    def __str__(self):
        return "Gstreamer Error: %s\nDebug Message: %s" % (self.err, self.debug)


class Encoder(object):

    """
    Encodes a video from Virtual Machine screenshots (jpg files).

    First, a directory with screenshots is inspected, and the screenshot sizes,
    normalized. After that, the video is encoded, using a gstreamer pipeline
    that goes like (using gstreamer terminology):

    multifilesrc -> jpegdec -> vp8enc -> webmmux -> filesink
    """

    def __init__(self, params, verbose=False):
        self.verbose = verbose
        self.params = params
        Gst.init(None)

    def convert_to_jpg(self, input_dir):
        """
        Convert .ppm files inside [input_dir] to .jpg files.

        :param input_dir: Directory to inspect.
        """
        image_files = glob.glob(os.path.join(input_dir, '*.ppm'))
        quality = self.params.get('avocado.args.run.video_encoding.jpeg_quality',
                                  defaults.video_encoding_jpeg_quality)
        for ppm_file in image_files:
            ppm_file_basename = os.path.basename(ppm_file)
            jpg_file_basename = ppm_file_basename[:-4] + '.jpg'
            jpg_file = os.path.join(input_dir, jpg_file_basename)
            i = Image.open(ppm_file)
            i.save(jpg_file, format="JPEG", quality=quality)
            os.remove(ppm_file)

    def get_most_common_image_size(self, input_dir):
        """
        Find the most common image size on a directory containing .jpg files.

        :param input_dir: Directory to inspect.
        """
        image_sizes = {}
        image_files = glob.glob(os.path.join(input_dir, '*.jpg'))
        for f in image_files:
            i = Image.open(f)
            if not image_sizes.has_key(i.size):
                image_sizes[i.size] = 1
            else:
                image_sizes[i.size] += 1

        most_common_size_counter = 0
        most_common_size = None
        for image_size, image_counter in image_sizes.items():
            if image_counter > most_common_size_counter:
                most_common_size_counter = image_counter
                most_common_size = image_size
        return most_common_size

    def normalize_images(self, input_dir):
        """
        Normalize images of different sizes so we can encode a video from them.

        :param input_dir: Directory with images to be normalized.
        """
        image_size = self.get_most_common_image_size(input_dir)
        if image_size is None:
            image_size = (800, 600)

        if self.verbose:
            log.debug('Normalizing image files to size: %s' % (image_size,))
        image_files = glob.glob(os.path.join(input_dir, '*.jpg'))
        for f in image_files:
            i = Image.open(f)
            if i.size != image_size:
                i.resize(image_size).save(f)

    def encode(self, input_dir, output_file):
        """
        Process the input files and output the video file.

        The encoding part of it is equivalent to

        gst-launch multifilesrc location=[input_dir]/%04d.jpg index=1
        caps='image/jpeg, framerate=(fraction)4/1' !
        jpegdec ! vp8enc ! webmmux ! filesink location=[output_file]

        :param input_dir: Directory with images to be encoded into a video.
        :param output_file: Path to the output video file.
        """
        self.convert_to_jpg(input_dir)
        self.normalize_images(input_dir)

        file_list = glob.glob(os.path.join(input_dir, '*.jpg'))
        no_files = len(file_list)
        if no_files == 0:
            if self.verbose:
                log.debug("Number of files to encode as video is zero")
            return
        index_list = []
        for ifile in file_list:
            index_list.append(int(re.findall(r"/+.*/(\d{4})\.jpg", ifile)[0]))
            index_list.sort()
        if self.verbose:
            log.debug('Number of files to encode as video: %s' % no_files)

        # Define the gstreamer pipeline
        pipeline = Gst.Pipeline()

        # Message bus - it allows us to control the end of the encoding process
        # asynchronously
        message_bus = pipeline.get_bus()
        message_bus.add_signal_watch()

        # Defining source properties (multifilesrc, jpegs and framerate)
        source = Gst.ElementFactory.make("multifilesrc", "multifilesrc")
        source_location = os.path.join(input_dir, "%04d.jpg")
        source.set_property('location', source_location)
        # The index property won't work in Fedora 21 Alpha, see bug:
        # https://bugzilla.gnome.org/show_bug.cgi?id=739472
        source.set_property('start-index', index_list[0])
        source_caps = Gst.caps_from_string('image/jpeg, framerate=(fraction)4/1')
        source.set_property('caps', source_caps)

        # Decoder element (jpeg format decoder)
        decoder = Gst.ElementFactory.make("jpegdec", "jpegdec")

        # Decoder element (vp8 format encoder)
        encoder = Gst.ElementFactory.make("vp8enc", "vp8enc")

        # Container (WebM container)
        container = Gst.ElementFactory.make("webmmux", "webmmux")

        # Defining output properties
        output = Gst.ElementFactory.make("filesink", "filesink")
        output.set_property('location', output_file)

        # Adding all elements to the pipeline
        pipeline.add(source)
        pipeline.add(decoder)
        pipeline.add(encoder)
        pipeline.add(container)
        pipeline.add(output)

        # Linking all elements
        source.link(decoder)
        decoder.link(encoder)
        encoder.link(container)
        container.link(output)

        # Set pipeline to Gst.State.PLAYING
        pipeline.set_state(Gst.State.PLAYING)

        # Wait until the stream stops
        err = None
        debug = None
        while True:
            msg = message_bus.timed_pop(Gst.CLOCK_TIME_NONE)
            t = msg.type
            if t == Gst.MessageType.EOS:
                pipeline.set_state(Gst.State.NULL)
                if self.verbose:
                    log.debug("Video %s encoded successfully" % output_file)
                break
            elif t == Gst.MessageType.ERROR:
                err, debug = msg.parse_error()
                pipeline.set_state(Gst.State.NULL)
                break

        if err is not None:
            raise EncodingError(err, debug)
