import os
from django.conf import settings
import shutil
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from management.models import ApplicationExtension, ApplicationContentType
from account.utils import validate_email, validate_text, validate_password, convert_to_kb, list_of_extensions, \
    list_of_content_types
import secrets
from account.models import Client, ValidatorBlock
from processor.serializers import ValidatorBlockSerializer
from PIL import Image, ImageOps
import cv2
from .utils import variance_of_laplacian, check_if_blur
# Create your views here.

class CreateValidationBlockView(APIView):
    """
    This endpoint is used to create, update, delete and read a validation block with all fields required on creation.

    List of fields:
        client_token, block_name, file_threshold, file_size_unit, number_of_images, image_dimension_threshold,
        image_height, allowed_extensions, content_types.
    """
    permission_classes = []

    def get(self, request):
        try:
            block_token = request.GET.get("block_token", None)

            if not block_token:
                return Response({"detail": "Set 'block_token'."}, status=HTTP_400_BAD_REQUEST)

            block = ValidatorBlock.objects.get(block_token=block_token)
            if block is not None:
                serializer = ValidatorBlockSerializer(instance=block, many=False).data
                return Response({"detail": serializer})

            return Response({"detail": f"Couldn't fetch validation block with '{block_token}'."})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)

    def post(self, request):
        """
            Used to add a Validation Block
        """
        try:
            client_token = request.data.get("client_token", None)
            block_name = request.data.get('block_name', None)
            file_threshold_size = request.data.get('file_threshold_size', None)  # Image size
            file_size_unit = request.data.get('file_size_unit', None)
            numb_of_images_per_process = request.data.get("number_of_images", None)
            image_height_dimension_threshold = request.data.get('image_height_dimension_threshold',
                                                                None)  # width and height checks in pixels
            image_width_dimension_threshold = request.data.get('image_width_dimension_threshold',
                                                               None)  # width and height checks in pixels

            block_token = secrets.token_urlsafe(15)
            allowed_extensions = request.data.get('allowed_extensions', [])
            content_types = request.data.get("content_types", [])

            allow_size_check = request.data.get("allow_dimension_check", False)
            allow_dimension_check = request.data.get("allow_dimension_check", False)
            allow_extension_check = request.data.get("allow_extension_check", False)
            allow_content_type_check = request.data.get("allow_content_type_check", False)
            allow_number_of_image_check = request.data.get("allow_number_of_image_check", False)
            allow_blurry_images = request.data.get("allow_blurry_images", False)

            if not client_token:
                return Response({"detail": "Set 'client_token'."}, status=HTTP_400_BAD_REQUEST)

            client = Client.objects.filter(client_token=client_token)

            if client.exists() and client.count() == 1:
                client = Client.objects.get(client_token=client_token)
            else:
                return Response({"detail": f"Invalid Client Token."}, status=HTTP_400_BAD_REQUEST)

            if not block_name:
                return Response({"detail": f"Set 'block_name'."}, status=HTTP_400_BAD_REQUEST)

            block = ValidatorBlock(block_name=str(block_name).title(), block_token=block_token, client=client)

            if allow_number_of_image_check:
                if not numb_of_images_per_process:
                    return Response({"detail": f"Set 'number_of_images'."}, status=HTTP_400_BAD_REQUEST)
                numb_of_images_per_process = int(numb_of_images_per_process)

                if numb_of_images_per_process > 20:
                    return Response({"detail": f"Enter a number lesser than 20 and greater than one."},
                                    status=HTTP_400_BAD_REQUEST)
                elif numb_of_images_per_process < 1:
                    return Response({"detail": f"Number of images per process should not be less than 1'."},
                                    status=HTTP_400_BAD_REQUEST)
                block.allow_number_of_image_check = allow_number_of_image_check

            if allow_size_check:
                if not file_threshold_size:
                    return Response({"detail": f"Set 'file_threshold_size'."}, status=HTTP_400_BAD_REQUEST)

                if not file_size_unit:
                    return Response({"detail": f"Set 'file_size_unit'."}, status=HTTP_400_BAD_REQUEST)
                file_size_unit = str(file_size_unit).lower()

                success, resp = convert_to_kb(unit=file_size_unit, value=file_threshold_size)  # Convert the Size (MB) to KB.

                if not success:
                    return Response({"detail": f"{resp}"}, status=HTTP_400_BAD_REQUEST)
                block.file_threshold_size = resp
                block.allow_size_check = allow_size_check

            if allow_dimension_check:
                if not image_height_dimension_threshold:
                    return Response({"detail": f"Set 'image_height_dimension_threshold'."}, status=HTTP_400_BAD_REQUEST)

                if not image_width_dimension_threshold:
                    return Response({"detail": f"Set 'image_width_dimension_threshold'."}, status=HTTP_400_BAD_REQUEST)
                block.allow_dimension_check = allow_dimension_check
                block.image_height_dimension_threshold = image_height_dimension_threshold
                block.image_width_dimension_threshold = image_width_dimension_threshold

            block.allow_blurry_images = allow_blurry_images
            block.save()

            if allow_extension_check:
                if not allowed_extensions:
                    return Response({"detail": f"Set 'allowed_extensions'."}, status=HTTP_400_BAD_REQUEST)
                block.allow_extension_check = allow_extension_check

                for id_ in allowed_extensions:
                    if id_ not in list_of_extensions:  # 'image/svg+xml' can be allowed later.
                        block.delete()  # Delete created block.
                        return Response(
                            {"detail": f"Invalid image extension '{id_}' ID."},
                            status=HTTP_400_BAD_REQUEST)

                    extension = ApplicationExtension.objects.get(id=id_)
                    block.allowed_extensions.add(extension)

            if allow_content_type_check:
                if not content_types:
                    return Response({"detail": f"Set 'content_types'."}, status=HTTP_400_BAD_REQUEST)
                block.allow_content_type_check = allow_content_type_check

                for typ_id in content_types:
                    if typ_id not in list_of_content_types:  # 'gif' and more can be allowed later.
                        block.delete()  # Delete created block.
                        return Response(
                            {"detail": f"Invalid image content_type '{typ_id}' ID."},
                            status=HTTP_400_BAD_REQUEST)

                    extension = ApplicationContentType.objects.get(id=typ_id)
                    block.content_type.add(extension)
            block.save()
            return Response({"detail": f"{block_name} Validation block has been created.",
                             "block_token": f"{block_token}"})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            client_token = request.data.get("client_token", None)
            block_name = request.data.get('block_name', None)
            block_token = request.data.get('block_token', None)
            file_threshold_size = request.data.get('file_threshold_size', None)  # Image size
            file_size_unit = request.data.get('file_size_unit', None)
            numb_of_images_per_process = request.data.get("number_of_images", None)
            image_height_dimension_threshold = request.data.get('image_height_dimension_threshold',
                                                                None)  # width and height checks in pixels
            image_width_dimension_threshold = request.data.get('image_width_dimension_threshold',
                                                               None)  # width and height checks in pixels
            allowed_extensions = request.data.get('allowed_extensions', [])
            content_types = request.data.get("content_types", [])

            allow_size_check = request.data.get("allow_size_check", False)
            allow_dimension_check = request.data.get("allow_dimension_check", False)
            allow_extension_check = request.data.get("allow_extension_check", False)
            allow_content_type_check = request.data.get("allow_content_type_check", False)
            allow_number_of_image_check = request.data.get("allow_number_of_image_check", False)
            allow_blurry_images = request.data.get("allow_blurry_images", False)

            if not client_token:
                return Response({"detail": "Set 'client_token'."}, status=HTTP_400_BAD_REQUEST)

            client = Client.objects.filter(client_token=client_token)

            if client.exists() and client.count() == 1:
                client = Client.objects.get(client_token=client_token)
            else:
                return Response({"detail": f"Invalid Client Token."}, status=HTTP_400_BAD_REQUEST)

            if not block_token:
                return Response({"detail": f"Set 'block_token'."}, status=HTTP_400_BAD_REQUEST)

            block = ValidatorBlock.objects.get(block_token=block_token, client=client)

            if block_name:
                block.block_name = block_name

            if allow_number_of_image_check:
                if not numb_of_images_per_process:
                    return Response({"detail": f"Set 'number_of_images'."}, status=HTTP_400_BAD_REQUEST)
                numb_of_images_per_process = int(numb_of_images_per_process)

                if numb_of_images_per_process > 20:
                    return Response({"detail": f"Enter a number lesser than 20 and greater than one."},
                                    status=HTTP_400_BAD_REQUEST)
                elif numb_of_images_per_process < 1:
                    return Response({"detail": f"Number of images per process should not be less than 1'."},
                                    status=HTTP_400_BAD_REQUEST)
                block.numb_of_images_per_process = numb_of_images_per_process
                block.allow_number_of_image_check = allow_number_of_image_check

            block.allow_number_of_image_check = allow_number_of_image_check  # False

            if allow_size_check:
                if not file_threshold_size:
                    return Response({"detail": f"Set 'file_threshold_size'."}, status=HTTP_400_BAD_REQUEST)

                if not file_size_unit:
                    return Response({"detail": f"Set 'file_size_unit'."}, status=HTTP_400_BAD_REQUEST)
                file_size_unit = str(file_size_unit).lower()

                success, file_size_value_or_err_msg = convert_to_kb(unit=file_size_unit,
                                                                    value=file_threshold_size)  # Convert the Size (MB) to KB.
                if not success:
                    return Response({"detail": f"{file_size_value_or_err_msg}"}, status=HTTP_400_BAD_REQUEST)
                block.file_threshold_size = file_threshold_size
                block.allow_size_check = allow_size_check
            block.allow_size_check = allow_size_check  # False

            if allow_dimension_check:
                if not image_height_dimension_threshold:
                    return Response({"detail": f"Set 'image_height_dimension_threshold'."}, status=HTTP_400_BAD_REQUEST)

                if not image_width_dimension_threshold:
                    return Response({"detail": f"Set 'image_width_dimension_threshold'."}, status=HTTP_400_BAD_REQUEST)
                block.image_height_dimension_threshold = image_height_dimension_threshold
                block.image_width_dimension_threshold = image_width_dimension_threshold
                block.allow_dimension_check = allow_dimension_check
            block.allow_dimension_check = allow_dimension_check  # False

            if allow_extension_check:
                if not allowed_extensions:
                    return Response({"detail": f"Set 'allowed_extensions'."}, status=HTTP_400_BAD_REQUEST)

                block.allowed_extensions.clear()
                for extension in allowed_extensions:
                    block.allowed_extensions.add(extension)
                block.allow_extension_check = allow_extension_check
            block.allow_extension_check = allow_extension_check  # False

            if allow_content_type_check:
                if not content_types:
                    return Response({"detail": f"Set 'content_types'."}, status=HTTP_400_BAD_REQUEST)

                block.content_type.clear()
                for content_type in content_types:
                    block.content_type.add(content_type)
                block.allow_content_type_check = allow_content_type_check
            block.allow_content_type_check = allow_content_type_check

            block.allow_blurry_images = allow_blurry_images
            block.save()
            return Response({"detail": "Validation Block has been updated."})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, token=None):
        try:
            if not token:
                return Response({"detail": "'token' is required."}, status=HTTP_400_BAD_REQUEST)

            block = ValidatorBlock.objects.get(block_token=token)

            if block is not None:
                block.delete()
                return Response({"detail": "Validation block has been deleted."}, status=HTTP_204_NO_CONTENT)
            return Response({"detail": "Validation block not found."})
        except (Exception,) as err:
            return Response({"detail": f"{err}"}, status=HTTP_400_BAD_REQUEST)


class ValidationView(APIView):
    permission_classes = []

    def post(self, request):
        """
            Synopsis: Use for running Validation on the number of images passed in.
            This lock is used to run validation on any number of images passed.
                1. Get "validation block token" from request body data.
                2. Run validation based on the specifications in the "Validation block".

                - Check for number of images passed against the "numb_of_images_per_process" field on the
                    'ValidatorBlock'.
        """
        try:
            client_token = request.data.get("client_token", None)
            block_token = request.data.get("block_token", None)

            if request.FILES.get("images", None) is None:
                return Response({"detail": "'images' field is required."}, status=HTTP_400_BAD_REQUEST)

            images = dict(request.FILES)['images']
            if not client_token:
                return Response({"detail": "'client_token' field is required."}, status=HTTP_400_BAD_REQUEST)

            if not block_token:
                return Response({"detail": "'block_token' field is required."}, status=HTTP_400_BAD_REQUEST)

            block = ValidatorBlock.objects.get(block_token=block_token)
            block_extensions = [str(ext_.extension_name).lower() for ext_ in block.allowed_extensions.all()]
            block_contents = [str(contents_.content_name).lower() for contents_ in block.content_type.all()]

            # 1. Check the number of images present in request header.

            if len(images) > block.numb_of_images_per_process:
                return Response({"description": f"requires a Maximum of {block.numb_of_images_per_process} images(s)"},
                                status=HTTP_400_BAD_REQUEST)

            # 2. Get the image details and Check image details again the block settings.
            for image in images:
                image_item = Image.open(image)

                # Check image extension.
                if block.allow_extension_check:
                    image_extension: str = image_item.format.lower()
                    if image_extension not in block_extensions:
                        return Response(
                            {"detail": f"Unacceptable image extension of '{image_extension}' for '{image.name}'."})

                #   Check Content Type
                if block.allow_content_type_check:
                    image_content_type: str = image.content_type
                    if image_content_type not in block_contents:
                        return Response(
                            {"detail": f"Unacceptable image content-type of {image_content_type} for image {image.name}."})
                # ------------------------------------------------------------------------------------------------------

                # Check image size against the specified block size.
                # 1. Pillow returns the image size in Bytes, so 1000 Bytes -> 1 Kilobytes

                if block.allow_size_check:
                    # convert Bytes to KB.
                    converted, value_or_errmsg = convert_to_kb(unit='b', value=image.size)
                    if not converted:
                        return Response({"detail": f"{value_or_errmsg}"}, status=HTTP_400_BAD_REQUEST)

                    if value_or_errmsg > block.file_threshold_size:
                        return Response({"detail": f"File size should be {float(block.file_threshold_size)}KB or less"},
                                        status=HTTP_400_BAD_REQUEST)

                # ------------------------------------------------------------------------------------------------------
                if block.allow_dimension_check:
                    # Check if the image height in pixel is less than the width specified in the Validation Block
                    if image_item.height < block.image_height_dimension_threshold:
                        return Response({
                            "detail": f"'{image.name}' height in pixels should be '{block.image_height_dimension_threshold}px' or less"},
                            status=HTTP_400_BAD_REQUEST)

                    # Check if the image width in pixel is less than the width specified in the Validation Block
                    if image_item.width < block.image_width_dimension_threshold:
                        return Response({
                            "detail": f"'{image.name}' height in pixels should be "
                                      f"'{block.image_height_dimension_threshold}px' or less"},
                            status=HTTP_400_BAD_REQUEST)

                if block.allow_blurry_images:
                    path_ = rf"{os.getcwd()}/images"
                    try:
                        if not os.path.exists(path_):
                            os.mkdir(f"{path_}")

                        # System only saves with JPEG type not JPG, so I did an Adjustment to change all JPSs to JPEG.
                        ext = "JPEG" if str(image.name).split(".")[-1].upper() == "JPG" else str(image.name).split(".")[
                            -1].upper()

                        # Save image to images/ folder.
                        image_item.save(fp=f"{path_}/{image.name}", format=ext)
                    except (FileNotFoundError, FileExistsError, Exception) as err:
                        # Log Error Message
                        shutil.rmtree(path_)

                    # Calculate Blurriness of an Image.
                    success, msg = check_if_blur(cv_image_instance=image_item, image=image, image_path=path_)

                    # Remove/Release the images from the image/ directory.
                    shutil.rmtree(path_)

                    if success is False:
                        return Response({"detail": f"'{image.name}' is {msg}",
                                         "description": f"The system detected a Blurry image '{image.name}', "
                                                        f"Please enter a clear image."}, status=HTTP_400_BAD_REQUEST)

            return Response({"detail": f"{len(images)} image has been validated." if len(
                images) == 1 else f"{len(images)} has been Validated successfully."})
        except (Exception,) as err:
            return Response({"detail": f"{err}."}, status=HTTP_400_BAD_REQUEST)


