from django.shortcuts import render, redirect
import zipfile
import pandas as pd
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import os
import tempfile
import shutil
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile, SimpleUploadedFile
from django.contrib.auth.decorators import login_required
from shop.models import *
from shop.forms import *
from custom.models import *
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Q

# Import data
@login_required()
def parse_datetime(value):
    try:
        return pd.to_datetime(value) if pd.notnull(value) and str(value).strip() else None
    except Exception:
        return None

@login_required()
def import_shops_view(request):
    preview_data = None
    if request.method == 'POST':
        action = request.POST.get('action')
        form = ShopImportForm(request.POST, request.FILES)
        if action == 'preview' and form.is_valid():
            file = request.FILES['file']
            df = pd.read_csv(file)
            request.session['csv_data'] = df.to_json(orient='records')  # Save to session
            # preview_data = df.head(20).to_dict(orient='records')  # Limit preview
            max_preview = min(500, len(df))
            preview_data = df.head(max_preview).to_dict(orient='records')

        elif action == 'confirm':
            json_records = request.session.get('csv_data')
            if json_records:
                df = pd.read_json(json_records, orient='records')


                municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
                admin_posts = {a.name.lower(): a for a in AdministrativePost.objects.all()}
                villages = {v.name.lower(): v for v in Village.objects.all()}
                aldeias = {a.name.lower(): a for a in Aldeia.objects.all()}
                channels = {c.name.lower(): c for c in Channel.objects.all()}
                with transaction.atomic():

                    for _, row in df.iterrows():
                        name=row.get('name_of_shop') or ''
                        owner=row.get('name_of_owner') or ''
                        contact=row.get('phone') or ''
                        center = municipalities.get(str(row.get('center', '')).strip().lower())
                        municipality = municipalities.get(str(row.get('district', '')).strip().lower())
                        admin_post = admin_posts.get(str(row.get('subdistrict', '')).strip().lower())
                        village = villages.get(str(row.get( 'suco', '')).strip().lower())
                        aldeia = aldeias.get(str(row.get('aldeia', '')).strip().lower())
                        latitude=row.get('latitude') if pd.notnull(row.get('latitude')) else None
                        longitude=row.get('longitude') if pd.notnull(row.get('longitude')) else None
                        dimension=row.get('dimension') or ''
                        kind_of_banner=row.get('kind_of_banner') or ''

                        print(f"Processing shop: {name}, Owner: {owner}, Contact: {contact}, "
                            f"Center: {center.id if center else 'None'}, Municipality: {municipality.id if municipality else 'None'}, "
                            f"Admin Post: {admin_post.id if admin_post else 'None'}, Village: {village.id if village else 'None'}, "
                            f"Aldeia: {aldeia.id if aldeia else 'None'}, Latitude: {latitude}, Longitude: {longitude}, "
                            f"Dimension: {dimension}, Kind of Banner: {kind_of_banner}, "
                            )

                        shop = Shop.objects.create(
                                name=name,
                                owner=owner,
                                contact=contact,
                                center=center,
                                municipality=municipality,
                                administrativepost=admin_post,
                                village=village,
                                aldeia=aldeia,
                                latitude=latitude,
                                longitude=longitude,
                                dimension=dimension,
                                kind_of_banner=kind_of_banner,
                            )
                        # many-to-many relationships
                        raw_channels = row.get('kind_of_channel', '')
                        for cname in str(raw_channels).split(','):
                            print(f"Processing channel: {cname.strip().lower()}")
                            c = channels.get(cname.strip().lower())
                            print(c.id)
                            if c:
                                shop.kind_of_channel.add(c)
                request.session.pop('csv_data', None)
                return redirect('shop-list')  # Replace with your success URL

    else:
        form = ShopImportForm()
    
    context = {
        'form': form,
        'preview_data': preview_data,
        "acShop": 'active',
        }
    return render(request, 'shop/import_data.html', context)

@login_required()
def import_shop_images_view(request):
    preview_data = []
    image_map = {}

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "confirm":
            df = pd.read_json(request.session.get("import_csv_data"), orient="records")
            image_names = request.session.get("import_image_names", [])
            uploaded_files = request.FILES.getlist("images")
            image_map = {f.name.split('/')[-1]: f for f in uploaded_files}

            with transaction.atomic():
                for row in df:
                    shop_name = row.get("shop_name", "").strip()
                    image_name = row.get("image", "").strip()
                    is_id = row.get("is_id", False)

                    shop = Shop.objects.filter(name__iexact=shop_name).first()
                    image_file = image_map.get(image_name) if image_name else None

                    if shop and image_file:
                        ShopImage.objects.create(
                            shop=shop,
                            image=image_file,
                            is_id=bool(is_id)
                        )
                    else:
                        print(f"[Skip] Missing shop or image: {shop_name}, {image_name}")

            request.session.pop("import_csv_data", None)
            request.session.pop("import_image_names", None)
            return redirect("shop-list")

        else:
            csv_file = request.FILES.get("csv_file")
            image_files = request.FILES.getlist("images")
            df = pd.read_csv(csv_file)

            image_map = {f.name.split('/')[-1]: f for f in image_files}
            image_names = list(image_map.keys())

            request.session["import_csv_data"] = df.to_json(orient="records")
            request.session["import_image_names"] = image_names

            for _, row in df.iterrows():
                shop_name = row.get("shop_name", "").strip()
                image_name = row.get("image", "").strip()
                is_id = row.get("is_id", False)
                shop = Shop.objects.filter(name__iexact=shop_name).first()
                image_file = image_map.get(image_name) if image_name else None

                preview_data.append({
                    "shop_name": shop_name,
                    "shop_found": "✅" if shop else "❌",
                    "image_name": image_name,
                    "image_found": "✅" if image_file else "❌",
                    "content_type": image_file.content_type if image_file else "-",
                    "size_kb": round(image_file.size / 1024, 1) if image_file else "-",
                    "is_id": is_id
                })

    return render(request, "shop/import_data_image.html", {
        "preview_data": preview_data,
        "acShop": 'active',
    })



@login_required()
def import_shop_images_view1(request):
    """Enhanced image import from folder - supports CSV/Excel with preview"""
    from shop.forms_image_import import ImageImportFolderForm
    
    preview_data = []
    imported_count = 0
    
    if request.method == 'POST':
        action = request.POST.get('action')
        form = ImageImportFolderForm(request.POST, request.FILES)
        
        if action == 'preview' and form.is_valid():
            data_file = request.FILES['data_file']
            file_type = form.cleaned_data['file_type']
            sheet_name = form.cleaned_data.get('sheet_name', '')
            image_files = request.FILES.getlist('images')
            
            # Build image map
            image_map = {f.name.split('/')[-1]: f for f in image_files}
            
            try:
                # Read data file (CSV or Excel)
                if file_type == 'csv':
                    df = pd.read_csv(data_file)
                elif file_type == 'excel':
                    try:
                        import openpyxl
                        sheet = sheet_name if sheet_name else 0
                        df = pd.read_excel(data_file, sheet_name=sheet, engine='openpyxl')
                    except ImportError:
                        form.add_error('data_file', 'Excel support not available. Please install openpyxl library')
                        return render(request, 'shop/import_data_image1.html', {'form': form, 'acShop': 'active'})
                    except Exception as excel_error:
                        form.add_error('data_file', f'Error reading Excel file: {str(excel_error)}')
                        return render(request, 'shop/import_data_image1.html', {'form': form, 'acShop': 'active'})
                
                # Save data and image files for confirmation
                request.session['image_import_data'] = df.to_json(orient='records')
                
                # Save image files to temporary location
                temp_dir = tempfile.mkdtemp(prefix='shop_import_')
                request.session['temp_image_dir'] = temp_dir
                
                image_files_info = {}
                for f in image_files:
                    filename = f.name.split('/')[-1]
                    temp_path = os.path.join(temp_dir, filename)
                    with open(temp_path, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    image_files_info[filename] = {
                        'size': f.size,
                        'content_type': f.content_type,
                        'temp_path': temp_path
                    }
                
                request.session['image_files_info'] = image_files_info
                
                # Generate preview with error checking
                municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
                processing_errors = []
                
                for idx, row in df.iterrows():
                    try:
                        shop_name = str(row.get("shop_name", "")).strip()
                        image_name = str(row.get("image_name", "")).strip()
                        image_type = str(row.get("image_type", "")).strip()
                        center_name = str(row.get('center', '')).strip().lower()
                        phone = str(row.get('phone', '')).strip()
                        
                        # Validate required fields
                        if not shop_name:
                            processing_errors.append(f"Row {idx + 2}: Missing shop name")
                            continue
                        if not image_name:
                            processing_errors.append(f"Row {idx + 2}: Missing image name")
                            continue
                            
                        center = municipalities.get(center_name)
                        shop = None
                        
                        if center:
                            shop = Shop.objects.filter(
                                name__iexact=shop_name, 
                                center=center, 
                                contact__iexact=phone
                            ).first()
                        
                        image_file = image_map.get(image_name)
                        
                        # Validate image file type
                        image_valid = True
                        if image_file:
                            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                            if image_file.content_type not in valid_types:
                                image_valid = False
                                processing_errors.append(f"Row {idx + 2}: Invalid image type {image_file.content_type}")
                        
                        preview_data.append({
                            "row_number": idx + 2,
                            "shop_name": shop_name,
                            "center_name": center_name,
                            "phone": phone,
                            "shop_found": "✅" if shop else "❌",
                            "image_name": image_name,
                            "image_found": "✅" if image_file and image_valid else "❌",
                            "content_type": image_file.content_type if image_file else "-",
                            "size_kb": round(image_file.size / 1024, 1) if image_file else "-",
                            "image_type": image_type,
                            "will_create_new": "✅" if shop and image_file and image_valid else "❌",
                            "imported": "❌",
                            "errors": []
                        })
                        
                    except Exception as e:
                        processing_errors.append(f"Row {idx + 2}: Unexpected error - {str(e)}")
                
                # Add processing errors to form if any
                if processing_errors:
                    for error in processing_errors[:5]:  # Show first 5 errors
                        form.add_error(None, error)
                    if len(processing_errors) > 5:
                        form.add_error(None, f"... and {len(processing_errors) - 5} more errors")
                
                # Add info about Django's automatic file renaming
                if any(row["will_create_new"] == "✅" for row in preview_data):
                    form.add_error(None, "Info: Django will automatically rename files with duplicate names to avoid conflicts.")
                    
            except pd.errors.EmptyDataError:
                form.add_error('data_file', 'The uploaded file is empty or has no readable data.')
            except pd.errors.ParserError as e:
                form.add_error('data_file', f'Error parsing file: {str(e)}. Please check the file format.')
            except Exception as e:
                form.add_error('data_file', f'Unexpected error reading file: {str(e)}')
                
        elif action == 'confirm':
            json_data = request.session.get('image_import_data')
            temp_image_dir = request.session.get('temp_image_dir')
            image_files_info = request.session.get('image_files_info', {})
            
            if not json_data or not temp_image_dir or not image_files_info:
                form.add_error(None, 'No preview data found. Please preview first.')
                return render(request, 'shop/import_data_image1.html', {'form': form, 'acShop': 'active'})
            
            df = pd.read_json(json_data, orient='records')
            
            # Create image map from temporary files
            image_map = {}
            for filename, info in image_files_info.items():
                temp_path = info.get('temp_path')
                if temp_path and os.path.exists(temp_path):
                    with open(temp_path, 'rb') as f:
                        image_file = SimpleUploadedFile(
                            name=filename,
                            content=f.read(),
                            content_type=info.get('content_type', 'image/jpeg')
                        )
                        image_map[filename] = image_file
            municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
            
            # Track import statistics
            stats = {
                'imported': 0,
                'skipped': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        shop_name = str(row.get("shop_name", "")).strip()
                        image_name = str(row.get("image_name", "")).strip()
                        image_type = str(row.get("image_type", "")).strip()
                        center_name = str(row.get('center', '')).strip().lower()
                        phone = str(row.get('phone', '')).strip()
                        
                        # Skip if missing required data
                        if not shop_name or not image_name:
                            stats['skipped'] += 1
                            continue
                        
                        center = municipalities.get(center_name)
                        if not center:
                            stats['skipped'] += 1
                            continue
                            
                        shop = Shop.objects.filter(
                            name__iexact=shop_name, 
                            center=center, 
                            contact__iexact=phone
                        ).first()
                        
                        if not shop:
                            stats['skipped'] += 1
                            continue
                        
                        image_file = image_map.get(image_name)
                        if not image_file:
                            stats['skipped'] += 1
                            continue
                        
                        # Check for existing image
                        existing_image = ShopImage.objects.filter(
                            shop=shop,
                            image_type=image_type,
                            delete_time__isnull=True
                        ).first()
                        
                        if existing_image:
                            # Update existing image
                            existing_image.image = image_file
                            existing_image.update_time = datetime.now()
                            existing_image.is_active = True
                            existing_image.save()
                            stats['updated'] += 1
                        else:
                            # Create new image
                            ShopImage.objects.create(
                                shop=shop,
                                image=image_file,
                                image_type=image_type,
                                update_time=datetime.now(),
                                is_active=True
                            )
                            stats['imported'] += 1
                            
                    except Exception as e:
                        stats['errors'].append(f"Row {idx + 2}: {str(e)}")
                        if len(stats['errors']) >= 10:  # Limit error reporting
                            break
            
            # Clear session data and cleanup temp files
            request.session.pop('image_import_data', None)
            request.session.pop('image_files_info', None)
            
            # Cleanup temporary files
            temp_dir = request.session.pop('temp_image_dir', None)
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    pass  # Ignore cleanup errors
            
            # Prepare success message
            success_parts = []
            if stats['imported']:
                success_parts.append(f"{stats['imported']} images imported")
            if stats['skipped']:
                success_parts.append(f"{stats['skipped']} items skipped")
            
            if success_parts:
                messages.success(request, f"Import completed: {', '.join(success_parts)}.")
            
            if stats['errors']:
                for error in stats['errors'][:3]:  # Show first 3 errors
                    messages.warning(request, error)
                if len(stats['errors']) > 3:
                    messages.warning(request, f"... and {len(stats['errors']) - 3} more errors occurred.")
            
            return redirect('shop-import-images')
    
    else:
        form = ImageImportFolderForm()
    
    return render(request, "shop/import_data_image1.html", {
        "form": form,
        "preview_data": preview_data,
        "imported_count": imported_count,
        "acShop": 'active',
    })

def resolve_nested(map_obj, *keys):
    ref = map_obj
    for key in keys:
        key = key.strip().lower()
        ref = ref.get(key)
        if ref is None:
            return None
    return ref

@login_required()
def import_shops_view1(request):
    preview_data = None
    has_missing = False
    imported_count = 0
    if request.method == 'POST':
        action = request.POST.get('action')
        form = ShopImportForm(request.POST, request.FILES)
        if action == 'preview' and form.is_valid():
            file = request.FILES['file']
            file_type = form.cleaned_data['file_type']
            sheet_name = form.cleaned_data.get('sheet_name', '')
            
            try:
                if file_type == 'csv':
                    df = pd.read_csv(file)
                elif file_type == 'excel':
                    try:
                        # Check if openpyxl is available
                        import openpyxl
                        # Use sheet name if provided, otherwise use first sheet (0)
                        sheet = sheet_name if sheet_name else 0
                        df = pd.read_excel(file, sheet_name=sheet, engine='openpyxl')
                    except ImportError:
                        form.add_error('file', 'Excel support not available. Please install openpyxl library: pip install openpyxl')
                        return render(request, 'shop/import_data.html', {'form': form, 'preview_data': preview_data, "acShop": 'active'})
                    except Exception as excel_error:
                        form.add_error('file', f'Error reading Excel file: {str(excel_error)}. Please ensure the file is not corrupted and the sheet name is correct.')
                        return render(request, 'shop/import_data.html', {'form': form, 'preview_data': preview_data, "acShop": 'active'})
                else:
                    form.add_error('file_type', 'Unsupported file type selected.')
                    return render(request, 'shop/import_data.html', {'form': form, 'preview_data': preview_data, "acShop": 'active'})
                
                request.session['csv_data'] = df.to_json(orient='records')  # Save to session
                max_preview = min(500, len(df))
                preview_data = df.head(max_preview).to_dict(orient='records')
            except pd.errors.EmptyDataError:
                form.add_error('file', 'The uploaded file is empty or has no readable data.')
            except pd.errors.ParserError as e:
                form.add_error('file', f'Error parsing file: {str(e)}. Please check the file format.')
            except Exception as e:
                form.add_error('file', f'Unexpected error reading file: {str(e)}')

        elif action == 'confirm':
            json_records = request.session.get('csv_data')
            if json_records:
                df = pd.read_json(json_records, orient='records')

                municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
                admin_posts_map = {}
                villages_map = {}
                aldeias_map = {}
                channels = {c.name.lower(): c for c in Channel.objects.all()}
                for ap in AdministrativePost.objects.select_related('municipality'):
                    muni = ap.municipality.name.lower()
                    admin_posts_map.setdefault(muni, {})[ap.name.lower()] = ap

                for v in Village.objects.select_related('administrativepost__municipality'):
                    muni = v.administrativepost.municipality.name.lower()
                    ap = v.administrativepost.name.lower()
                    villages_map.setdefault(muni, {}).setdefault(ap, {})[v.name.lower()] = v

                for a in Aldeia.objects.select_related('village__administrativepost__municipality'):
                    muni = a.village.administrativepost.municipality.name.lower()
                    ap = a.village.administrativepost.name.lower()
                    suco = a.village.name.lower()
                    aldeias_map.setdefault(muni, {}).setdefault(ap, {}).setdefault(suco, {})[a.name.lower()] = a
                imported_count = 0
                has_missing = False

                with transaction.atomic():

                    for _, row in df.iterrows():
                        name = row.get('name_of_shop') or ''
                        owner = row.get('name_of_owner') or ''
                        contact = row.get('phone') or ''
                        center_name = str(row.get('center', '')).strip().lower()
                        municipality_name = str(row.get('district', '')).strip().lower()
                        admin_post_name = str(row.get('subdistrict', '')).strip().lower()
                        village_name = str(row.get('suco', '')).strip().lower()
                        aldeia_name = str(row.get('aldeia', '')).strip().lower()
                        latitude = row.get('latitude') if pd.notnull(row.get('latitude')) else None
                        longitude = row.get('longitude') if pd.notnull(row.get('longitude')) else None
                        dimension = row.get('dimension') or ''
                        kind_of_banner = row.get('kind_of_banner') or ''
                        center = municipalities.get(center_name)

                        center = municipalities.get(center_name)
                        municipality = municipalities.get(municipality_name)
                        admin_post = resolve_nested(admin_posts_map, municipality_name, admin_post_name)
                        village = resolve_nested(villages_map, municipality_name, admin_post_name, village_name)
                        aldeia = resolve_nested(aldeias_map, municipality_name, admin_post_name, village_name, aldeia_name)

                        shop = Shop.objects.create(
                                name=name,
                                owner=owner,
                                contact=contact,
                                center=center,
                                municipality=municipality,
                                administrativepost=admin_post,
                                village=village,
                                aldeia=aldeia,
                                latitude=latitude,
                                longitude=longitude,
                                dimension=dimension,
                                kind_of_banner=kind_of_banner,
                            )
                        # many-to-many relationships
                        raw_channels = row.get('kind_of_channel', '')
                        for cname in str(raw_channels).split(';'):
                            print(f"Processing channel: {cname.strip().lower()}")
                            c = channels.get(cname.strip().lower())
                            if c:
                                print(c.id)
                                shop.kind_of_channel.add(c)
                        imported_count += 1
                if has_missing:
                    imported_count = 0

                print(f"Imported count: {imported_count}")
                request.session.pop('csv_data', None)
                return redirect('shop-list')  # Replace with your success URL

    else:
        form = ShopImportForm()

    context = {
        'form': form,
        'preview_data': preview_data,
        "acShop": 'active',
        }
    return render(request, 'shop/import_data.html', context)


TEMP_IMAGE_DIR = "media/temp_shop_images"  # Make sure this exists and is writable

@login_required()
def ShopImageImportZip(request):
    """Enhanced ZIP image import - supports CSV/Excel with better preview"""
    from shop.forms_image_import import ImageImportZipForm
    
    preview_data = []
    imported_count = 0

    if request.method == 'POST':
        action = request.POST.get('action')
        form = ImageImportZipForm(request.POST, request.FILES)

        if action == 'preview' and form.is_valid():
            zip_file = request.FILES['zip_file']
            data_file = request.FILES['data_file'] 
            file_type = form.cleaned_data['file_type']
            sheet_name = form.cleaned_data.get('sheet_name', '')

            # Extract ZIP images temporarily
            fs = FileSystemStorage(location=TEMP_IMAGE_DIR)
            image_map = {}

            try:
                with zipfile.ZipFile(zip_file) as zf:
                    for file_name in zf.namelist():
                        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                            continue  # Skip non-image files
                        base_name = file_name.split('/')[-1]  # Get filename without path
                        with zf.open(file_name) as f:
                            filepath = fs.save(base_name, f)
                            image_map[base_name] = fs.path(filepath)
            except Exception as e:
                form.add_error('zip_file', f"Failed to extract ZIP file: {str(e)}")
                return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})

            try:
                # Read data file (CSV or Excel)
                if file_type == 'csv':
                    df = pd.read_csv(data_file)
                elif file_type == 'excel':
                    try:
                        import openpyxl
                        sheet = sheet_name if sheet_name else 0
                        df = pd.read_excel(data_file, sheet_name=sheet, engine='openpyxl')
                    except ImportError:
                        form.add_error('data_file', 'Excel support not available. Please install openpyxl library')
                        return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})
                    except Exception as excel_error:
                        form.add_error('data_file', f'Error reading Excel file: {str(excel_error)}')
                        return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})
                        
            except pd.errors.EmptyDataError:
                form.add_error('data_file', 'The uploaded file is empty or has no readable data.')
                return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})
            except pd.errors.ParserError as e:
                form.add_error('data_file', f'Error parsing file: {str(e)}. Please check the file format.')
                return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})
            except Exception as e:
                form.add_error('data_file', f'Unexpected error reading file: {str(e)}')
                return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})

            # Generate preview with duplicate checking
            municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
            duplicate_images = set()
            processing_errors = []

            for idx, row in df.iterrows():
                try:
                    shop_name = str(row.get("shop_name", "")).strip()
                    image_name = str(row.get("image_name", "")).strip()
                    image_type = str(row.get("image_type", "")).strip()
                    center_name = str(row.get("center", "")).strip().lower()
                    phone = str(row.get("phone", "")).strip()
                    
                    # Validate required fields
                    if not shop_name:
                        processing_errors.append(f"Row {idx + 2}: Missing shop name")
                        continue
                    if not image_name:
                        processing_errors.append(f"Row {idx + 2}: Missing image name")
                        continue
                    
                    center = municipalities.get(center_name)
                    image_path = image_map.get(image_name)
                    
                    shop = None
                    existing_image = None
                    duplicate_status = ""
                    
                    if center:
                        shop = Shop.objects.filter(
                            name__iexact=shop_name,
                            center=center,
                            contact__iexact=phone
                        ).first()
                        
                        # Check for existing image
                        if shop:
                            existing_image = ShopImage.objects.filter(
                                shop=shop,
                                image_type=image_type,
                                delete_time__isnull=True
                            ).first()
                            
                            if existing_image:
                                duplicate_status = "⚠️ Will update"
                                duplicate_images.add(f"{shop_name}-{image_type}")

                    # Validate image file
                    file_size_str = "-"
                    image_valid = bool(image_path)
                    if image_path and os.path.exists(image_path):
                        try:
                            file_size = os.path.getsize(image_path)
                            file_size_str = f"{file_size / 1024:.1f} KB"
                            
                            # Check file size (max 10MB)
                            if file_size > 10 * 1024 * 1024:
                                image_valid = False
                                processing_errors.append(f"Row {idx + 2}: Image too large (>{file_size/1024/1024:.1f}MB)")
                        except OSError:
                            image_valid = False
                            processing_errors.append(f"Row {idx + 2}: Cannot access image file")

                    preview_data.append({
                        "row_number": idx + 2,
                        "shop_name": shop_name,
                        "center_name": center_name,
                        "phone": phone,
                        "shop_found": "✅" if shop else "❌",
                        "image_name": image_name,
                        "image_found": "✅" if image_valid else "❌",
                        "image_path": image_path or "",
                        "image_type": image_type,
                        "file_size": file_size_str,
                        "duplicate_status": duplicate_status,
                        "imported": "❌"
                    })
                    
                except Exception as e:
                    processing_errors.append(f"Row {idx + 2}: Unexpected error - {str(e)}")

            # Add processing errors to form if any
            if processing_errors:
                for error in processing_errors[:5]:  # Show first 5 errors
                    form.add_error(None, error)
                if len(processing_errors) > 5:
                    form.add_error(None, f"... and {len(processing_errors) - 5} more errors")
            
            # Add duplicate warning
            if duplicate_images:
                form.add_error(None, f"Warning: Found {len(duplicate_images)} existing images that will be updated")

            # Save preview data and form data
            request.session['zip_preview_data'] = preview_data
            request.session['zip_form_data'] = {
                'file_type': file_type,
                'sheet_name': sheet_name
            }

        elif action == 'confirm':
            preview_data = request.session.get('zip_preview_data', [])
            if not preview_data:
                form.add_error(None, "No preview data found. Please preview before confirming.")
                return render(request, "shop/import/importImageZip.html", {"form": form, "acShop": 'active'})

            municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
            
            # Track import statistics
            stats = {
                'imported': 0,
                'updated': 0,
                'skipped': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for record in preview_data:
                    if record["shop_found"] == "✅" and record["image_found"] == "✅":
                        try:
                            center = municipalities.get(record["center_name"])
                            if not center:
                                stats['skipped'] += 1
                                continue
                                
                            shop = Shop.objects.filter(
                                name__iexact=record["shop_name"],
                                center=center,
                                contact__iexact=record["phone"]
                            ).first()

                            if shop and record["image_path"] and os.path.exists(record["image_path"]):
                                # Check for existing image
                                existing_image = ShopImage.objects.filter(
                                    shop=shop,
                                    image_type=record["image_type"],
                                    delete_time__isnull=True
                                ).first()
                                
                                with open(record["image_path"], "rb") as f:
                                    image_file = SimpleUploadedFile(record["image_name"], f.read())
                                    
                                    if existing_image:
                                        # Update existing image
                                        existing_image.image = image_file
                                        existing_image.update_time = datetime.now()
                                        existing_image.is_active = True
                                        existing_image.save()
                                        record["imported"] = "✅ Updated"
                                        stats['updated'] += 1
                                    else:
                                        # Create new image
                                        ShopImage.objects.create(
                                            shop=shop,
                                            image=image_file,
                                            image_type=record["image_type"],
                                            update_time=datetime.now(),
                                            is_active=True
                                        )
                                        record["imported"] = "✅ New"
                                        stats['imported'] += 1
                            else:
                                record["imported"] = "❌ Shop/Image not found"
                                stats['skipped'] += 1
                                
                        except Exception as e:
                            record["imported"] = f"❌ Error: {str(e)[:50]}..."
                            stats['errors'].append(f"{record['shop_name']}: {str(e)}")
                    else:
                        record["imported"] = "❌ Validation failed"
                        stats['skipped'] += 1
            
            # Cleanup temp files
            for record in preview_data:
                image_path = record.get("image_path")
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        pass  # Ignore cleanup errors
                        
            # Clear session data
            request.session.pop('zip_preview_data', None)
            request.session.pop('zip_form_data', None)
            
            # Prepare detailed success/warning messages
            success_parts = []
            if stats['imported']:
                success_parts.append(f"{stats['imported']} new images imported")
            if stats['updated']:
                success_parts.append(f"{stats['updated']} existing images updated")
            if stats['skipped']:
                success_parts.append(f"{stats['skipped']} items skipped")
            
            if success_parts:
                messages.success(request, f"ZIP import completed: {', '.join(success_parts)}.")
            
            if stats['errors']:
                for error in stats['errors'][:3]:  # Show first 3 errors
                    messages.warning(request, error)
                if len(stats['errors']) > 3:
                    messages.warning(request, f"... and {len(stats['errors']) - 3} more errors occurred.")
            
            return redirect('shop-import-images_zip')
    
    else:
        form = ImageImportZipForm()

    return render(request, "shop/import/importImageZip.html", {
        "form": form,
        "title": "Import Images from ZIP File",
        "preview_data": preview_data,
        "imported_count": imported_count,
        "visible_fields": ["shop_name", "shop_found", "image_name", "image_found", "image_type", "file_size", "imported"],
        "acShop": 'active',
    })
