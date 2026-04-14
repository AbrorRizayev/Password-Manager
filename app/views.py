from django.db.models import Count
import pandas as pd
from django.http import HttpResponse
from .models import Credential
from .utils import encrypt_password, decrypt_password
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re


def get_password_strength(password):
    if not password:
        return "None", "gray"

    score = 0
    if len(password) >= 8: score += 1
    if any(c.isupper() for c in password): score += 1
    if any(c.isdigit() for c in password): score += 1
    if any(c in "!@#$%^&*()_+-=" for c in password): score += 1

    if score <= 1:
        return "Weak", "#dc2626"  # Qizil
    elif score == 2:
        return "Fair", "#ca8a04"  # Sariq
    elif score >= 3:
        return "Strong", "#16a34a"  # Yashil
    return "Weak", "#dc2626"

def login_view(request):
    if request.user.is_authenticated:
        return redirect('vault:vault')


    if request.method == "POST":
        u_name = request.POST.get('username')
        p_word = request.POST.get('password')

        user = authenticate(request, username=u_name, password=p_word)

        if user is not None:
            login(request, user)
            # BU YERNI TEKSHIRING: 'vault' emas, 'vault:vault' bo'lishi kerak
            return redirect('vault:vault')
        else:
            messages.error(request, "Username yoki Master Password noto'g'ri!")

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('vault:login')


@login_required(login_url='vault:login')
def add_credential(request):
    if request.method == "POST":
        service = request.POST.get('service_name')
        user_name = request.POST.get('username')
        raw_password = request.POST.get('password')
        url = request.POST.get('url')

        # Parolni shifrlash
        encrypted_pw = encrypt_password(raw_password)

        Credential.objects.create(
            user=request.user,
            service_name=service,
            username=user_name,
            encrypted_password=encrypted_pw,
            url=url
        )
        return redirect('vault:vault')
    existing_passwords = []
    for item in Credential.objects.filter(user=request.user):
        existing_passwords.append(decrypt_password(item.encrypted_password))
    return render(request, 'add_entry.html', {'existing_hashes': existing_passwords})


@login_required(login_url='vault:login')
def vault_view(request):
    # 1. Bazadan foydalanuvchiga tegishli ma'lumotlarni olish
    credentials = Credential.objects.filter(user=request.user)

    # 2. Filtrlash (Sizning kodingiz)
    category_filter = request.GET.get('category')
    if category_filter:
        credentials = credentials.filter(category=category_filter)

    # 3. Qidiruv (Sizning kodingiz)
    search_query = request.GET.get('q')
    if search_query:
        credentials = credentials.filter(service_name__icontains=search_query)

    # 4. PAROLLARNI YECHISH VA KUCHINI ANIQLASH (Yangi qism)
    for item in credentials:
        try:
            # Parolni shifrdan yechamiz
            plain_pass = decrypt_password(item.encrypted_password)
            item.plaintext_password = plain_pass

            # PAROL KUCHINI ANIQLASH (Dashboard uchun)
            strength, color = get_password_strength(plain_pass)
            item.strength_label = strength
            item.strength_color = color

        except Exception:
            item.plaintext_password = ""
            item.strength_label = "Unknown"
            item.strength_color = "gray"

    # 5. Duplicate Alert (Sizning kodingiz)
    duplicates = (
        Credential.objects.filter(user=request.user)
        .values('encrypted_password')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    duplicate_passwords = [item['encrypted_password'] for item in duplicates]

    # 6. Kategoriyalar (Sizning kodingiz)
    categories = Credential.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    categories = [c for c in categories if c]

    # 7. Context (Barcha ma'lumotlar jamlangan)
    context = {
        'credentials': credentials,
        'categories': categories,
        'duplicate_passwords': duplicate_passwords,
    }
    return render(request, 'vault.html', context)

@login_required(login_url='vault:login')
def edit_credential(request, pk):
    item = get_object_or_404(Credential, id=pk, user=request.user)

    if request.method == "POST":
        # Barcha maydonlarni POST so'rovidan olib bazaga saqlaymiz
        item.service_name = request.POST.get('service_name')
        item.username = request.POST.get('username')
        item.url = request.POST.get('url')

        # MANA BU QATORNI QO'SHING:
        item.category = request.POST.get('category')

        new_pw = request.POST.get('password')
        if new_pw:
            item.encrypted_password = encrypt_password(new_pw)

        item.save()
        return redirect('vault:vault')

    decrypted_pw = decrypt_password(item.encrypted_password)
    return render(request, 'edit_entry.html', {'item': item, 'password': decrypted_pw})

@login_required(login_url='vault:login')
def delete_credential(request, pk):
    # Bu yerda user=request.user bo'lishi shart,
    # aks holda boshqa birovning parolini o'chirib yuborish mumkin
    item = get_object_or_404(Credential, pk=pk, user=request.user)

    if request.method == 'POST':
        item.delete()
        return redirect('vault:vault')

    return render(request, 'confirm_delete.html', {'item': item})



@login_required
def export_credentials(request):
    if request.method == "POST":
        # Tanlangan ID'larni olamiz
        selected_ids = request.POST.getlist('selected_items')

        if not selected_ids:
            messages.error(request, "Hech bo'lmaganda bitta elementni tanlang!")
            return redirect('vault:vault')

        # Tanlangan ma'lumotlarni bazadan olamiz
        credentials = Credential.objects.filter(id__in=selected_ids, user=request.user)

        data = []
        for item in credentials:
            data.append({
                'Service Name': item.service_name,
                'URL': item.url,
                'Username': item.username,
                'Password': decrypt_password(item.encrypted_password),
                'Category': item.category,
                'Created At': item.created_at.replace(tzinfo=None) if item.created_at else ''
            })

        # Pandas orqali Excel yaratish
        df = pd.DataFrame(data)

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="TeamVault_Backup.xlsx"'

        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Credentials')

        return response

    return redirect('vault:vault')


from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

@login_required(login_url='vault:login')
def settings_view(request):
    if request.method == 'POST':
        # Master parolni o'zgartirish qismi
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            messages.error(request, "Hozirgi master parol noto'g'ri!")
        elif new_password != confirm_password:
            messages.error(request, "Yangi parollar bir-biriga mos kelmadi!")
        elif len(new_password) < 8:
            messages.error(request, "Yangi parol kamida 8 ta belgidan iborat bo'lishi kerak!")
        else:
            request.user.set_password(new_password)
            request.user.save()
            # Parol o'zgargandan keyin sessiya tugab qolmasligi uchun
            update_session_auth_hash(request, request.user)
            messages.success(request, "Master parol muvaffaqiyatli o'zgartirildi!")
            return redirect('vault:settings')

    return render(request, 'settings.html')
