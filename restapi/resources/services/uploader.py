# -*- coding: utf-8 -*-

""" Upload data to APIs """

import os
import shutil
import subprocess as shell
from flask import request, redirect, url_for, abort, send_from_directory
from werkzeug import secure_filename
from ... import htmlcodes as hcodes
from ..base import ExtendedApiResource
from ... import get_logger

UPLOAD_FOLDER = '/uploads'
INTERPRETER = 'python'
ZBIN = '/zoomify/processor/ZoomifyFileProcessor.py'
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logger = get_logger(__name__)


# Save files http://API/upload
class Uploader(ExtendedApiResource):

    allowed_exts = ['png', 'jpg', 'jpeg', 'tiff']

    def allowed_file(self, filename):
        return '.' in filename \
            and filename.rsplit('.', 1)[1].lower() in self.allowed_exts

    def post(self):

        if 'file' not in request.files:
            return "No files specified"

        myfile = request.files['file']
        logger.info("Received file request for '%s'" % myfile)

        if myfile and self.allowed_file(myfile.filename):
            filename = secure_filename(myfile.filename)

            print("FILE IS ", filename)

#             # Check file name
#             abs_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             app.logger.info("A file allowed: "+ filename + ". Path: " +abs_file)

#             if os.path.exists(abs_file):

# # #####################
# # # DEBUG
# #                 os.remove(abs_file)
# # #####################

#                 app.logger.warn("Already existing file: "+ abs_file)
#                 abort(hcodes.HTTP_BAD_REQUEST, "File '"+ filename +"' already exists. " + \
#                     "Please change your file name and retry.")

#             # Save the file
#             myfile.save(abs_file)

#             # Make zoomify object and thumbnail
#             app.logger.info("Elaborate image")
#             # Proc via current shell
#             cmd = [INTERPRETER, ZBIN, abs_file]
#             proc = shell.Popen(cmd, stdout=shell.PIPE, stderr=shell.PIPE)
#             out, err = proc.communicate()
#             # Handle output
#             if proc.returncode == 0:
#                 if out != None and out != "":
#                     app.logger.info("Comm output: " + out)
#             else:
#                 app.logger.critical("Failed to process image " + abs_file + \
#                     ". Error: " + err)
#                 abort(hcodes.HTTP_BAD_REQUEST, "Could not process file")

#             # Default redirect is to 302 state, which makes client
#             # think that response was unauthorized....
#             # see http://dotnet.dzone.com/articles/getting-know-cross-origin
#             return redirect(url_for('uploaded_file', filename='/' + filename),
#                 hcodes.HTTP_OK_BASIC)

#     return '''
#     <!doctype html>
#     <title>Uploader</title> <h2>Uploader</h2> Empty. Just for receiving!<br>
#     '''
        return True

# ###########################################
# # http://API/uploader/filename
# @app.route(UPLOAD_RESOURCE + '/<filename>', methods=['GET', 'DELETE'])
# def uploaded_file(filename):

#     app.logger.info("Specific request: " + request.method + ", " + filename)

#     abs_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#     if request.method == 'DELETE':

#         # Check file existence
#         if not os.path.exists(abs_file):
#             app.logger.critical("Not existing: "+ abs_file)
#             abort(hcodes.HTTP_BAD_NOTFOUND, "File '"+ filename +"' not found. " + \
#                 "Please change your file name and retry.")

#         # Remove zoomified directory
#         filebase, fileext = os.path.splitext(abs_file)
#         if os.path.exists(filebase):
#             shutil.rmtree(filebase)
#             app.logger.warn("Removed: "+ filebase +" [extension '"+fileext+"']")

#         # Remove the real file
#         os.remove(abs_file)
#         app.logger.warn("Removed: "+ abs_file)

#         return "Deleted", hcodes.HTTP_OK_NORESPONSE

#     # To get?
#     elif request.method == 'GET':
#         app.logger.info("Should provide: "+ abs_file)
#         return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

#     return ''' <!doctype html> <title>Uploader</title> Empty<br> '''
