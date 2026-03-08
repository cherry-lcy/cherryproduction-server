import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url
import os
from werkzeug.utils import secure_filename
import tempfile
import time

class CloudinaryService:
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET'],
            secure=True
        )
        self.app = app
    
    def upload_audio(self, audio_file, title, artist):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                audio_file.save(temp_file.name)
                
                upload_result = cloudinary.uploader.upload(
                    temp_file.name,
                    resource_type="video",
                    public_id=f"songs/{artist}_{title}",
                    folder="music_site/audio",
                    tags=[artist, "music", "audio"]
                )
                
                os.unlink(temp_file.name)
                
                return {
                    'url': upload_result['secure_url'],
                    'public_id': upload_result['public_id'],
                    'duration': upload_result.get('duration', 0),
                    'format': upload_result.get('format', 'mp3'),
                    'bytes': upload_result.get('bytes', 0),
                    'created_at': upload_result.get('created_at')
                }
        except Exception as e:
            print(f"Fail to upload audio: {e}")
            return None
    
    def upload_image(self, image_file, title, folder="covers"):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                image_file.save(temp_file.name)
                
                upload_result = cloudinary.uploader.upload(
                    temp_file.name,
                    resource_type="image",
                    public_id=f"{folder}/{title}",
                    folder="music_site/images",
                    tags=[title, "image"]
                )
                
                os.unlink(temp_file.name)
                
                return {
                    'url': upload_result['secure_url'],
                    'public_id': upload_result['public_id'],
                    'width': upload_result.get('width'),
                    'height': upload_result.get('height'),
                    'format': upload_result.get('format'),
                    'bytes': upload_result.get('bytes', 0),
                    'created_at': upload_result.get('created_at')
                }
        except Exception as e:
            print(f"Fail to upload image: {e}")
            return None
    
    def upload_pdf(self, pdf_file, title, artist):
        try:
            original_filename = secure_filename(pdf_file.filename)
            file_ext = os.path.splitext(original_filename)[1].lower()
            
            if file_ext != '.pdf':
                print(f"Error: File is not PDF: {file_ext}")
                return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                pdf_file.save(temp_file.name)
                
                folder_path = "music_site/pdf"
                safe_title = secure_filename(title)
                public_id = f"{safe_title}_{int(time.time())}"
                
                upload_result = cloudinary.uploader.upload(
                    temp_file.name,
                    resource_type="raw",
                    public_id=public_id,
                    folder=folder_path,
                    tags=[title, "pdf"],
                    context={
                        'caption': title,
                        'alt': title,
                        'original_filename': original_filename
                    }
                )
                
                os.unlink(temp_file.name)
                
                return {
                    'url': upload_result['secure_url'],
                    'public_id': upload_result['public_id'],
                    'format': upload_result.get('format', 'pdf'),
                    'bytes': upload_result.get('bytes', 0),
                    'created_at': upload_result.get('created_at'),
                    'folder': folder_path,
                    'title': title,
                    'artist': artist,
                    'original_filename': original_filename
                }
                
        except Exception as e:
            print(f"Fail to upload PDF: {e}")
            return None
    
    def get_all_images(self, max_results=100):
        try:
            result = cloudinary.api.resources(
                resource_type="image",
                type="upload",
                prefix="music_site/images",
                max_results=max_results
            )
            
            images = []
            for resource in result.get('resources', []):
                images.append({
                    'public_id': resource['public_id'],
                    'url': resource['secure_url'],
                    'width': resource.get('width'),
                    'height': resource.get('height'),
                    'format': resource['format'],
                    'bytes': resource['bytes'],
                    'created_at': resource['created_at'],
                    'tags': resource.get('tags', [])
                })
            
            return images
        except Exception as e:
            print(f"Fail to get images: {e}")
            return []
    
    def get_files_by_folder(self, folder, resource_type="all", max_results=100):
        try:
            if resource_type == "all":
                all_files = []
                for rt in ["image", "video", "raw"]:
                    try:
                        result = cloudinary.api.resources(
                            resource_type=rt,
                            type="upload",
                            prefix=folder,
                            max_results=max_results
                        )
                        for resource in result.get('resources', []):
                            all_files.append(self._format_resource(resource, rt))
                    except:
                        continue
                return all_files
            else:
                result = cloudinary.api.resources(
                    resource_type=resource_type,
                    type="upload",
                    prefix=folder,
                    max_results=max_results
                )
                
                files = []
                for resource in result.get('resources', []):
                    files.append(self._format_resource(resource, resource_type))
                
                return files
        except Exception as e:
            print(f"Fail to get files by folder: {e}")
            return []
    
    def _format_resource(self, resource, resource_type):
        base_info = {
            'public_id': resource['public_id'],
            'url': resource['secure_url'],
            'format': resource['format'],
            'bytes': resource['bytes'],
            'created_at': resource['created_at'],
            'tags': resource.get('tags', []),
            'resource_type': resource_type
        }

        if resource_type == "image":
            base_info.update({
                'width': resource.get('width'),
                'height': resource.get('height')
            })
        elif resource_type == "video":
            base_info.update({
                'duration': resource.get('duration', 0)
            })
        elif resource_type == "raw":
            context = resource.get('context', {}).get('custom', {})
            base_info.update({
                'title': context.get('caption', ''),
                'original_filename': context.get('original_filename', '')
            })
        
        return base_info
    
    
    def get_public_id_from_url(self, url):
        try:
            parts = url.split('/upload/')
            if len(parts) < 2:
                return None
            
            path_part = parts[1]
            if path_part.startswith('v'):
                path_part = '/'.join(path_part.split('/')[1:])

            public_id_with_ext = path_part.split('?')[0]
            public_id = '.'.join(public_id_with_ext.split('.')[:-1])
            
            return public_id
        except Exception as e:
            print(f"Fail to extract public_id from URL: {e}")
            return None
    
    def get_resource_type_from_url(self, url):
        if '/image/' in url or '/image/upload/' in url:
            return "image"
        elif '/video/' in url or '/video/upload/' in url:
            return "video"
        elif '/raw/' in url or '/raw/upload/' in url:
            return "raw"
        else:
            return "raw"  # 默认
    
    def get_file_info_by_url(self, url):
        try:
            public_id = self.get_public_id_from_url(url)
            if not public_id:
                return None
            
            resource_type = self.get_resource_type_from_url(url)
            
            result = cloudinary.api.resource(
                public_id,
                resource_type=resource_type
            )
            
            return self._format_resource(result, resource_type)
        except Exception as e:
            print(f"Fail to get file info by URL: {e}")
            return None
    
    def get_file_info_by_public_id(self, public_id, resource_type="raw"):
        try:
            result = cloudinary.api.resource(
                public_id,
                resource_type=resource_type
            )
            return self._format_resource(result, resource_type)
        except Exception as e:
            print(f"Fail to get file info by public_id: {e}")
            return None
    
    def delete_file_by_url(self, url):
        try:
            public_id = self.get_public_id_from_url(url)
            if not public_id:
                return False
            
            resource_type = self.get_resource_type_from_url(url)
            
            return self.delete_file(public_id, resource_type)
        except Exception as e:
            print(f"Fail to delete file by URL: {e}")
            return False
    
    def delete_file(self, public_id, resource_type="raw"):
        try:
            result = cloudinary.uploader.destroy(
                public_id, 
                resource_type=resource_type
            )
            return result['result'] == 'ok'
        except Exception as e:
            print(f"Fail to delete file: {e}")
            return False
    
    def delete_files_by_prefix(self, prefix, resource_type="all"):
        try:
            if resource_type == "all":
                types = ["image", "video", "raw"]
            else:
                types = [resource_type]
            
            success = True
            for rt in types:
                try:
                    result = cloudinary.api.delete_resources_by_prefix(
                        prefix,
                        resource_type=rt
                    )
                    if result.get('deleted'):
                        print(f"Deleted {len(result['deleted'])} {rt} files")
                except Exception as e:
                    print(f"Error deleting {rt} files: {e}")
                    success = False
            
            return success
        except Exception as e:
            print(f"Fail to delete files by prefix: {e}")
            return False
    
    def search_files(self, query, resource_type="all", max_results=100):
        try:
            search = cloudinary.Search()
            
            if resource_type != "all":
                search.expression(f"resource_type:{resource_type} AND {query}")
            else:
                search.expression(query)
            
            search.max_results(max_results)
            
            result = search.execute()
            
            files = []
            for resource in result.get('resources', []):
                rt = resource['resource_type']
                files.append(self._format_resource(resource, rt))
            
            return files
        except Exception as e:
            print(f"Fail to search files: {e}")
            return []
    
    
    def get_optimized_url(self, public_id, width=None, height=None, resource_type="raw"):
        if resource_type == "raw":
            url, _ = cloudinary_url(
                public_id,
                resource_type="raw",
                secure=True
            )
            return url
        elif resource_type == "image":
            if width and height:
                url, _ = cloudinary_url(
                    public_id,
                    width=width,
                    height=height,
                    crop="fill",
                    gravity="auto",
                    fetch_format="auto",
                    quality="auto"
                )
            else:
                url, _ = cloudinary_url(
                    public_id,
                    fetch_format="auto",
                    quality="auto"
                )
            return url
        elif resource_type == "video":
            url, _ = cloudinary_url(
                public_id,
                resource_type="video",
                fetch_format="auto",
                quality="auto"
            )
            return url
        
    def get_optimized_url_from_url(self, url, width=None, height=None):
        public_id = self.get_public_id_from_url(url)
        resource_type = self.get_resource_type_from_url(url)
        
        if public_id:
            return self.get_optimized_url(public_id, width, height, resource_type)
        return url