# -*- coding: utf-8 -*-

""" Upload data to APIs """

import os
import shutil
# import subprocess as shell
from flask import request, send_from_directory
from werkzeug import secure_filename
from ... import htmlcodes as hcodes
from ... import get_logger
from confs.config import UPLOAD_FOLDER, PY2_INTERPRETER

logger = get_logger(__name__)


######################################
# Create images part for zoomification
class ZoomEnabling(object):

    _zbin = UPLOAD_FOLDER + '/pyimgs/processor/ZoomifyFileProcessor.py'
    _images_exts = ['png', 'jpg', 'jpeg', 'tiff', 'tif']

    def split_dir_and_extension(self, filepath):
        filebase, fileext = os.path.splitext(filepath)
        return filebase, fileext.strip('.')

    def process_zoom(self, filename):
        """
        Make zoomify object + a small thumbnail
        """

        # Check Zoomify binaries
        if not os.path.exists(self._zbin):
            logger.critical("Zoomify is not available at: %s" % self._zbin)
            return False

        # Check Extension for image
        _, ext = self.split_dir_and_extension(filename)
        if ext.lower() not in self._images_exts:
            logger.warning("Extension is not an image: %s" % ext)
            return False

        # Process via current shell
        import subprocess as shell
        cmd = [PY2_INTERPRETER, self._zbin, filename]

        try:
            proc = shell.Popen(cmd, stdout=shell.PIPE, stderr=shell.PIPE)
            out, err = proc.communicate()
            # Handle output
            if proc.returncode == 0:
                if out is not None and out != "":
                    logger.debug("Zoom output: %s" % out)
                    return True
            else:
                logger.critical(
                    "Failed to process image '%s'. Error: \n '%s' "
                    % (filename, err))
        except Exception as e:
            logger.critical(
                "Failed to process image '%s'. Error: \n '%s' "
                % (filename, e))

        return False


######################################
# Save files http://API/upload
class Uploader(ZoomEnabling):
#class Uploader(ZoomEnabling, EXTENDEDAPI!):

    ZOOMIFY_ENABLE = False
    allowed_exts = []
    # allowed_exts = ['png', 'jpg', 'jpeg', 'tiff']

    def allowed_file(self, filename):
        if len(self.allowed_exts) < 1:
            return True
        return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in self.allowed_exts

    @staticmethod
    def absolute_upload_file(filename, subfolder=None, onlydir=False):
        if subfolder is not None:
            filename = os.path.join(subfolder, filename)
            dir = os.path.join(UPLOAD_FOLDER, subfolder)
            if not os.path.exists(dir):
                os.mkdir(dir)
        abs_file = os.path.join(UPLOAD_FOLDER, filename)  # filename.lower())
        if onlydir:
            return os.path.dirname(abs_file)
        return abs_file

    def download(self, filename=None, subfolder=None, get=False):

        if not get:
            return self.response(
                "No flow chunks for now", code=hcodes.HTTP_OK_ACCEPTED)

        if filename is None:
            return self.response(
                "No filename specified to download", fail=True)

        path = self.absolute_upload_file(
            filename, subfolder=subfolder, onlydir=True)
        logger.info("Provide '%s' from '%s' " % (filename, path))

        return send_from_directory(path, filename)

    def upload(self, subfolder=None):

        if 'file' not in request.files:
            return self.response("No files specified", fail=True)

        myfile = request.files['file']

        # ## IN CASE WE WANT TO CHUNK
        # ##parser = reqparse.RequestParser()
        # &flowChunkNumber=1
        # &flowChunkSize=1048576&flowCurrentChunkSize=1367129
        # &flowTotalSize=1367129
        # &flowIdentifier=1367129-IMG_4364CR2jpg
        # &flowFilename=IMG_4364.CR2.jpg
        # &flowRelativePath=IMG_4364.CR2.jpg
        # &flowTotalChunks=1

        # Check file extension?
        if not self.allowed_file(myfile.filename):
            return self.response(
                "File extension not allowed", fail=True)

        # Check file name
        filename = secure_filename(myfile.filename)
        abs_file = self.absolute_upload_file(filename, subfolder)
        logger.info("File request for [%s](%s)" % (myfile, abs_file))

        # ## IMPORTANT note:
        # If you are going to receive chunks here there could be problems.
        # In fact a chunk will truncate the connection
        # and make a second request.
        # You will end up with having already the file
        # But corrupted...
        if os.path.exists(abs_file):
            # os.remove(abs_file)  # an option to force removal?
            logger.warn("Already exists")
            return self.response(
                "File '" + filename + "' already exists. Please " +
                "change its name and retry.",
                fail=True, code=hcodes.HTTP_BAD_REQUEST)

        # Save the file
        try:
            myfile.save(abs_file)
            logger.debug("Absolute file path should be '%s'" % abs_file)
        except Exception:
            return self.response(
                "Failed to write uploaded file",
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        # Check exists
        if not os.path.exists(abs_file):
            return self.response(
                {"Server file system": "Unable to recover the uploaded file"},
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        ########################
        # Let the user decide about zoomify inside the JSON configuration
        # This variable can be modified in the child endpoint

        if self.ZOOMIFY_ENABLE:
            if self.process_zoom(abs_file):
                logger.info("Zoomified the image")
            else:
                os.unlink(abs_file)     # Remove the file!
                return self.response(
                    {"Image operation": "Image pre-scaling for zoom failed"},
                    fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

        # Extra info
        ftype = None
        fcharset = None
        try:
            # Check the type
            from plumbum.cmd import file
            out = file["-ib", abs_file]()
            tmp = out.split(';')
            ftype = tmp[0].strip()
            fcharset = tmp[1].split('=')[1].strip()
        except Exception:
            logger.warning("Unknown type for '%s'" % abs_file)

        ########################
        # ## Final response

        # Default redirect is to 302 state, which makes client
        # think that response was unauthorized....
        # see http://dotnet.dzone.com/articles/getting-know-cross-origin

        return self.response({
                'filename': filename,
                'meta': {'type': ftype, 'charset': fcharset}
            }, code=hcodes.HTTP_OK_BASIC)

    def remove(self, filename, subfolder=None, skip_response=False):
        """ Remove the file if requested """

        abs_file = self.absolute_upload_file(filename, subfolder)

        # Check file existence
        if not os.path.exists(abs_file):
            logger.critical("File '%s' not found" % abs_file)
            return self.response(
                "File requested does not exists",
                fail=True, code=hcodes.HTTP_BAD_NOTFOUND)

        # Remove zoomified directory
        filebase, fileext = os.path.splitext(abs_file)
        if self.ZOOMIFY_ENABLE and os.path.exists(filebase):
            try:
                shutil.rmtree(filebase)
                logger.warn("Removed dir '%s' " %
                            filebase + " [extension '" + fileext + "']")
            except Exception as e:
                logger.critical("Cannot remove zoomified:\n '%s'" % str(e))

        # Remove the real file
        try:
            os.remove(abs_file)
        except Exception:
            logger.critical("Cannot remove local file %s" % abs_file)
            return self.response(
                "Failed to remove file",
                code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)
        logger.warn("Removed '%s' " % abs_file)

        if skip_response:
            return

        return self.response(
            "Deleted", code=hcodes.HTTP_OK_BASIC)
