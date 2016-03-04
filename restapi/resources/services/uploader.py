# -*- coding: utf-8 -*-

""" Upload data to APIs """

import os
# import shutil
# import subprocess as shell
from flask import request  # , send_from_directory
from werkzeug import secure_filename
from ... import htmlcodes as hcodes
from ..base import ExtendedApiResource
from ... import get_logger
from confs.config import INTERPRETER, UPLOAD_FOLDER


logger = get_logger(__name__)


######################################
# Create images part for zoomification
class ZoomEnabling(object):

    _zbin = '/zoomify/processor/ZoomifyFileProcessor.py'

    def preprocess(self, filename):
        """
        Make zoomify object + a small thumbnail
        """

        #Should i check Extension for image?

        # Process via current shell
        import subprocess as shell
        cmd = [INTERPRETER, self._zbin, filename]
        proc = shell.Popen(cmd, stdout=shell.PIPE, stderr=shell.PIPE)
        out, err = proc.communicate()

        # Handle output
        if proc.returncode == 0:
            if out is not None and out != "":
                logger.debug("Zoom output: %s" % out)
        else:
            logger.critical(
                "Failed to process image '%s'. Error: \n '%s' "
                % (filename, err))
        return proc.returncode


######################################
# Save files http://API/upload
class Uploader(ExtendedApiResource):

    allowed_exts = ['png', 'jpg', 'jpeg', 'tiff']

    @staticmethod
    def absolute_upload_file(filename):
        return os.path.join(UPLOAD_FOLDER, filename.lower())

    def allowed_file(self, filename):
        return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in self.allowed_exts

    def get(self, filename=None):

        if filename is not None:
            abs_file = self.absolute_upload_file(filename)
            logger.info("Provide '%s' " % abs_file)
            # return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
            return "Not implemented yet", hcodes.HTTP_OK_NORESPONSE

        return "No flow chunks for now", hcodes.HTTP_OK_NORESPONSE

    def post(self):

        if 'file' not in request.files:
            return "No files specified"

        myfile = request.files['file']

        if not self.allowed_file(myfile.filename):
            return "File extension not allowed", hcodes.HTTP_BAD_REQUEST

        # Check file name
        filename = secure_filename(myfile.filename)
        abs_file = self.absolute_upload_file(filename)
        logger.info("File request for [%s](%s)" % (myfile, abs_file))

        if os.path.exists(abs_file):
            # os.remove(abs_file) # ??
            logger.warn("Already exists")
            return "File '" + filename + "' already exists. Please " + \
                "change its name and retry.", hcodes.HTTP_BAD_REQUEST

        # Save the file
        try:
            myfile.save(abs_file)
        except Exception:
            return "Failed to save file", hcodes.HTTP_DEFAULT_SERVICE_FAIL

# TO FIX:
# Let the user decide about zoomify inside the JSON configuration

        # If image and user_enabled_zoomify

        # abort(hcodes.HTTP_BAD_REQUEST, "Could not process file")
# TO FIX

        # Default redirect is to 302 state, which makes client
        # think that response was unauthorized....
        # see http://dotnet.dzone.com/articles/getting-know-cross-origin
        return "Uploaded", hcodes.HTTP_OK_BASIC

    def delete(self, filename):
        """ Remove the file if requested """

        abs_file = self.absolute_upload_file(filename)

        # Check file existence
        if not os.path.exists(abs_file):
            logger.critical("File '%s' not found" % abs_file)
            return "File requested does not exists", hcodes.HTTP_BAD_NOTFOUND

#         # Remove zoomified directory
#         filebase, fileext = os.path.splitext(abs_file)
#         if os.path.exists(filebase):
#             shutil.rmtree(filebase)
#             logger.warn("Removed dir '%s' " % \
#    filebase +" [extension '"+fileext+"']")

        # Remove the real file
        try:
            os.remove(abs_file)
        except Exception:
            return "Failed to save file", hcodes.HTTP_DEFAULT_SERVICE_FAIL
        logger.warn("Removed '%s' " % abs_file)

        return "Deleted", hcodes.HTTP_OK_NORESPONSE
