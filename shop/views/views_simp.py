from django.shortcuts import render, redirect
import zipfile
import pandas as pd
from datetime import datetime
from django.core.files.storage import FileSystemStorage
import os
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
    preview_data = []
    has_missing = False
    imported_count = 0
    just_preview = request.POST.get("just_preview") == "on"


    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        image_files = request.FILES.getlist("images")

        # Build image map for fast lookup
        image_map = {f.name.split('/')[-1]: f for f in image_files}

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return render(request, "shop/import_data_image.html", {
                "error": f"CSV parsing failed: {str(e)}"
            })
        municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
        for mun in municipalities.values():
            print(f"Municipality: {mun.name} with ID: {mun.id}")
        # shops = {s.name.lower(): s for s in Shop.objects.all()}
        if not just_preview:
            with transaction.atomic():
                for _, row in df.iterrows():
                    shop_name = str(row.get("shop_name", "")).strip()
                    image_name = str(row.get("image_name", "")).strip()
                    image_type = str(row.get("image_type", "")).strip()
                    center = municipalities.get(str(row.get('center', '')).strip().lower())
                    phone = row.get('phone') or ''
                    add_time = datetime.now()
                    print(f"Processing shop: {shop_name}, Center: {center}, Phone: {phone}, Image: {image_name}, Time: {add_time}")
                    # is_id = bool(row.get("is_id", False))

                    shop = Shop.objects.filter(name__iexact=shop_name, center__name__iexact=center, contact__iexact=phone).first()
                    image_file = image_map.get(image_name)
                    if not shop or not image_file:
                        has_missing = True
                    if shop and image_file:
                        # print(f"Importing image for shop: {shop.name} with {shop.id}, Image: {image_file.name} in time {add_time}")
                        ShopImage.objects.create(
                            shop=shop,
                            image=image_file,
                            image_type=image_type,
                            update_time=add_time,
                            is_active=True
                            # is_id=is_id
                        )
                        imported_count += 1

                    preview_data.append({
                        "shop_name": shop_name,
                        "shop_found": "✅" if shop else "❌",
                        "image_name": image_name,
                        "image_found": "✅" if image_file else "❌",
                        "content_type": image_file.content_type if image_file else "-",
                        "size_kb": image_file.size if image_file else "-",
                        "imported": "✅" if shop and image_file else "❌"
                    })
                    
        else:
            # Only generate preview
            for _, row in df.iterrows():
                shop_name = str(row.get("shop_name", "")).strip()
                image_name = str(row.get("image", "")).strip()
                shop_name = str(row.get("shop_name", "")).strip()
                image_name = str(row.get("image_name", "")).strip()
                center = municipalities.get(str(row.get('center', '')).strip().lower())
                phone = row.get('phone') or ''

                shop = Shop.objects.filter(name__iexact=shop_name, center__name__iexact=center, contact__iexact=phone).first()
                image_file = image_map.get(image_name)

                preview_data.append({
                    "shop_name": shop_name,
                    "shop_found": "✅" if shop else "❌",
                    "image_name": image_name,
                    "image_found": "✅" if image_file else "❌",
                    "content_type": image_file.content_type if image_file else "-",
                    "size_kb": image_file.size if image_file else "-",
                    "imported": "❌"
                })
        if has_missing:
            imported_count = 0
            for record in preview_data:
                if record["imported"] == "✅":
                    record["imported"] = "❌"


        return render(request, "shop/import_data_image1.html", {
            "preview_data": preview_data,
            "imported_count": imported_count,
            "just_preview": just_preview,
            "acShop": 'active',
        })

    return render(request, "shop/import_data_image1.html")

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
    preview_data = []
    imported_count = 0

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'preview':
            zip_file = request.FILES.get('zip_file')
            data_file = request.FILES.get('data_file')
            file_type = request.POST.get('file_type')
            sheet_index = int(request.POST.get('sheet_index', 1)) - 1

            # Save ZIP files temporarily
            fs = FileSystemStorage(location=TEMP_IMAGE_DIR)
            image_map = {}

            try:
                with zipfile.ZipFile(zip_file) as zf:
                    for file_name in zf.namelist():
                        if not file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            continue  # Skip non-image files
                        with zf.open(file_name) as f:
                            filepath = fs.save(file_name.split('/')[-1], f)
                            image_map[file_name.split('/')[-1]] = fs.path(filepath)
            except Exception as e:
                return render(request, "shop/import/importImageZip.html", {
                    "error": f"Failed to extract ZIP file: {str(e)}"
                })

            try:
                if file_type == "csv":
                    df = pd.read_csv(data_file)
                elif file_type == "excel":
                    df = pd.read_excel(data_file, sheet_name=sheet_index)
                else:
                    raise Exception("Invalid file type")
            except Exception as e:
                return render(request, "shop/import/importImageZip.html", {
                    "error": f"Failed to read CSV/Excel: {str(e)}"
                })

            municipalities = {m.name.lower(): m for m in Municipality.objects.all()}

            for _, row in df.iterrows():
                shop_name = str(row.get("shop_name", "")).strip()
                image_name = str(row.get("image_name", "")).strip()
                image_type = str(row.get("image_type", "")).strip()
                center_name = str(row.get("center", "")).strip().lower()
                phone = str(row.get("phone", "")).strip()
                center = municipalities.get(center_name)
                image_path = image_map.get(image_name)

                shop = Shop.objects.filter(
                    name__iexact=shop_name,
                    center__name__iexact=center.name if center else "",
                    contact__iexact=phone
                ).first()

                preview_data.append({
                    "shop_name": shop_name,
                    "center_name": center_name,
                    "phone": phone,
                    "shop_found": "✅" if shop else "❌",
                    "image_name": image_name,
                    "image_found": "✅" if image_path else "❌",
                    "image_path": image_path or "",
                    "image_type": image_type,
                    "imported": "❌"
                })

            request.session['preview_data'] = preview_data

        elif action == 'confirm':
            preview_data = request.session.get('preview_data', [])
            if not preview_data:
                return render(request, "shop/import/importImageZip.html", {
                    "error": "No preview data found. Please preview before confirming."
                })

            with transaction.atomic():
                for record in preview_data:
                    if record["shop_found"] == "✅" and record["image_found"] == "✅":
                        center = Municipality.objects.filter(name__iexact=record["center_name"]).first()
                        shop = Shop.objects.filter(
                            name__iexact=record["shop_name"],
                            center__name__iexact=center.name if center else "",
                            contact__iexact=record["phone"]
                        ).first()

                        try:
                            with open(record["image_path"], "rb") as f:
                                image_file = SimpleUploadedFile(record["image_name"], f.read())
                                print(f"Importing image: {record['image_name']} for shop: {record['shop_name']} (center: {record['center_name']}, phone: {record['phone']}) from path: {record['image_path']}, type: {record['image_type']}")
                                ShopImage.objects.create(
                                    shop=shop,
                                    image=image_file,
                                    image_type=record["image_type"],
                                    update_time=datetime.now(),
                                    is_active=True
                                )
                            record["imported"] = "✅"
                            imported_count += 1
                        except Exception as e:
                            record["imported"] = f"❌ Error: {e}"
            
            for record in preview_data:
                image_path = record.get("image_path")
                if image_path and os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        print(f"Failed to delete temp image: {image_path}, Error: {e}")
            request.session.pop('preview_data', None)
            return redirect('shop-import-images_zip')
    print(request.session.get('preview_data'))

    return render(request, "shop/import/importImageZip.html", {
        "title":"Import Image use .zip",
        "preview_data": preview_data,
        "imported_count": imported_count,
        "visible_fields": ["shop_name", "shop_found", "image_name", "image_found", "image_type", "imported"],
        "acShop": 'active',
    })
