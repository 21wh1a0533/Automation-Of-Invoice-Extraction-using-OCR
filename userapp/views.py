from django.shortcuts import render, redirect , get_object_or_404
from django.contrib import messages
from pdf2image import convert_from_bytes
from userapp.models import *
import random
import urllib.parse, urllib.request, ssl
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import urllib.request
import urllib.parse
from django.contrib.auth import logout
from django.core.mail import send_mail
import os
import random
from django.conf import settings
from userapp.models import *
from django.core.files.storage import default_storage
from django.utils.datastructures import MultiValueDictKeyError
from userapp.models import *


def generate_otp(length=4):
    otp = "".join(random.choices("0123456789", k=length))
    return otp


def user_logout(request):
    logout(request)
    messages.info(request, "Logout Successfully ")
    return redirect("user_login")

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')




def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request,'about.html')



def contact(request):
    return render(request,'contact.html')



def user_register(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password') 
        phone_number = request.POST.get('phone_number')
        age = request.POST.get('age')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('user_register') 
        user = User(
            full_name=full_name,
            email=email,
            password=password, 
            phone_number=phone_number,
            age=age,
            address=address,
            photo=photo
        )
        otp = generate_otp()
        user.otp = otp
        user.save()
        subject = "OTP Verification for Account Activation"
        message = f"Hello {full_name},\n\nYour OTP for account activation is: {otp}\n\nIf you did not request this OTP, please ignore this email."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        request.session["id_for_otp_verification_user"] = user.pk
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        messages.success(request, "Otp is sent your mail and phonenumber !")
        return redirect("user_otp")
    return render(request,"user-register.html")



def user_otp(request):
    otp_user_id = request.session.get("id_for_otp_verification_user")
    if not otp_user_id:
        messages.error(request, "No OTP session found. Please try again.")
        return redirect("user_register")
    if request.method == "POST":
        entered_otp = "".join(
            [
                request.POST["first"],
                request.POST["second"],
                request.POST["third"],
                request.POST["fourth"],
            ]
        )
        try:
            user = User.objects.get(id=otp_user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please try again.")
            return redirect("user_register")
        if user.otp == entered_otp:
            user.otp_status = "Verified"
            user.save()
            messages.success(request, "OTP verification successful!")
            return redirect("user_login")
        else:
            messages.error(request, "Incorrect OTP. Please try again.")
            return redirect("user_otp")
    return render(request,"user-otp.html")



def user_login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        try:
            user = User.objects.get(email=email)
            if user.password != password:
                messages.error(request, "Incorrect password.")
                return redirect("user_login")
            if user.status == "Accepted":
                if user.otp_status == "Verified":
                    request.session["user_id_after_login"] = user.pk
                    messages.success(request, "Login successful!")
                    return redirect("user_dashboard")
                else:
                    new_otp = generate_otp()
                    user.otp = new_otp
                    user.otp_status = "Not Verified"
                    user.save()
                    subject = "New OTP for Verification"
                    message = f"Your new OTP for verification is: {new_otp}"
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]
                    send_mail(
                        subject, message, from_email, recipient_list, fail_silently=False
                    )
                    messages.warning(
                        request,
                        "OTP not verified. A new OTP has been sent to your email and phone.",
                    )
                    request.session["id_for_otp_verification_user"] = user.pk
                    return redirect("user_otp")
            else:
                messages.success(request, "Your Account is Not Accepted by Admin Yet")
                return redirect("user_login")
        except User.DoesNotExist:
            messages.error(request, "No User Found.")
            return redirect("user_login")
    return render(request,"user-login.html")




def user_dashboard(request):
    return render(request,"user_dashboard.html")

# import os
# import openai
# import PyPDF2
# from openai import ChatCompletion
# from django.conf import settings
# from django.shortcuts import render
# from django.http import JsonResponse

# # Set the API key from your Django settings (for now, as you prefer)
# openai.api_key = settings.OPENAI_API_KEY

# def pdf_upload(request):
#     """
#     Display the invoice upload form and process the file upload.
#     Extracts text from a PDF invoice and stores it in the session.
#     """
#     if request.method == "POST":
#         pdf_file = request.FILES.get("pdf_file")
#         if pdf_file and pdf_file.content_type == "application/pdf":
#             extracted_text = extract_text_from_pdf(pdf_file)
#             # Store the extracted text in the session for later use in follow-up chat.
#             request.session['extracted_text'] = extracted_text
#             context = {"extracted_text": extracted_text}
#             return render(request, "pdf_result.html", context)
#         else:
#             # Pass an error message back to the template
#             return render(request, "pdf.html", {"error": "Please upload a valid PDF file."})
#     return render(request, "pdf.html")

# def extract_text_from_pdf(pdf_file):
#     """
#     Extract text from an uploaded PDF file using PyPDF2's PdfReader.
#     Note: For scanned documents, consider using OCR (e.g., pytesseract).
#     """
#     extracted_text = ""
#     try:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)
#         # Loop through each page in the PDF file
#         for page in pdf_reader.pages:
#             # The new method is extract_text(), not extractText()
#             text = page.extract_text()
#             if text:
#                 extracted_text += text
#     except Exception as e:
#         extracted_text = "Error extracting text: " + str(e)
#     return extracted_text

# def chat_invoice(request):
#     if request.method == "POST":
#         user_question = request.POST.get("question")
#         extracted_text = request.session.get("extracted_text", "")
#         if not extracted_text:
#             return JsonResponse({"error": "No invoice data found. Please upload an invoice first."}, status=400)

#         messages = [
#             {"role": "system", "content": "You are an assistant specialized in analyzing invoices and financial documents."},
#             {"role": "system", "content": f"Invoice details: {extracted_text}"},
#             {"role": "user", "content": user_question}
#         ]
#         try:
#             response = ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=messages,
#                 temperature=0.5,
#                 max_tokens=200
#             )
#             answer = response.choices[0].message.content
#             return JsonResponse({"answer": answer})
#         except Exception as e:
#             return JsonResponse({"error": f"API error: {str(e)}"}, status=500)
#     return JsonResponse({"error": "Invalid request method."}, status=400)



import os
import requests
import PyPDF2
import pytesseract
from PIL import Image
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import csv
import os
from django.http import HttpResponse
from docx import Document
from django.shortcuts import render
from django.conf import settings
from builtins import PendingDeprecationWarning
from django.core.mail import EmailMessage










def share_invoice(request, invoice_id):
    """
    Handle sharing the invoice via email.
    """
    # Get the invoice based on the ID
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    # Get the email from the form data
    recipient_email = request.POST.get("email")

    if recipient_email:
        # Send email with the invoice attached
        subject = f"Invoice {invoice.id} from {invoice.user.full_name}"
        message = f"Dear User, \n\nPlease find attached the invoice {invoice.id}.\n\nBest regards,\nSmart Invoice AI"

        # Create email message with attachment (PDF file)
        email = EmailMessage(
            subject=subject,
            body=message,
            to=[recipient_email],
        )
        email.attach(invoice.pdf_file.name, invoice.pdf_file.read(), 'application/pdf')
        
        try:
            email.send()
            messages.success(request,"Invoice sent successfully.")
            return redirect("history")
        except Exception as e:
            messages.error(request,str(e))
            return redirect("history")

    return redirect("history")





import io
import re

def download_invoice(request):
    """
    Handle the download request for different file formats (txt, json, docx, pdf, csv, html).
    """
    # Get the extracted text from session or other sources
    extracted_text = request.session.get("extracted_text", "No extracted text available.")
    
    if not extracted_text:
        return HttpResponse("No extracted text found.", status=404)

    # Get the file format from the request
    file_format = request.GET.get("format", "txt")

    # Prepare the response based on the file format
    if file_format == "txt":
        response = HttpResponse(extracted_text, content_type="text/plain")
        response["Content-Disposition"] = 'attachment; filename="invoice.txt"'

    elif file_format == "json":
        data = {"extracted_text": extracted_text}
        response = HttpResponse(json.dumps(data), content_type="application/json")
        response["Content-Disposition"] = 'attachment; filename="invoice.json"'

    elif file_format == "docx":
        doc = Document()
        doc.add_paragraph(extracted_text)
        doc_path = os.path.join(settings.MEDIA_ROOT, "invoice.docx")
        doc.save(doc_path)

        response = HttpResponse(open(doc_path, "rb"), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response["Content-Disposition"] = 'attachment; filename="invoice.docx"'

    elif file_format == "pdf":
        # You can generate PDF using ReportLab or similar library here
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="invoice.pdf"'
        # PDF generation logic should go here
        # For simplicity, you can return an empty PDF or generate a proper PDF

    elif file_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="invoice.csv"'
        
        
            
    elif file_format == "html":
        html_content = f"<html><body><pre>{extracted_text}</pre></body></html>"
        response = HttpResponse(html_content, content_type="text/html")
        response["Content-Disposition"] = 'attachment; filename="invoice.html"'

    else:
        return HttpResponse("Invalid format.", status=400)

    return response


DEFAULT_REJECTION = "I can only answer questions related to the invoice details."

def pdf_upload(request):
    """
    Display the upload form, process PDF/image upload, 
    extract text using PyPDF2 (for PDF) or Tesseract (for images).
    """
    if request.method == "POST":
        file = request.FILES.get("file")
        print("DEBUG: Received file:", file)

        if file:
            file_type = file.content_type
            extracted_text = ""

            # Handle PDF files
            if file_type == "application/pdf":
                extracted_text = extract_text_from_pdf(file)

            # Handle image files (JPG, PNG)
            elif file_type in ["image/jpeg", "image/png"]:
                extracted_text = extract_text_from_image(file)

            # If no valid file type
            else:
                return JsonResponse({"error": "Please upload a valid PDF or image file."}, status=400)

            print("DEBUG: Extracted text:", extracted_text)

            # Store the uploaded file and extracted text in the database
            user_id = request.session.get('user_id_after_login')
            user = User.objects.get(pk=user_id)

            invoice = Invoice.objects.create(
                user=user,
                pdf_file=file,
                extracted_text=extracted_text
            )
            print(f"DEBUG: Created invoice with id {invoice.id} for user {user.id}")

            request.session['extracted_text'] = extracted_text
            request.session['conversation'] = []

            context = {
                "extracted_text": extracted_text,
                "conversation": request.session.get("conversation", [])
            }

            return render(request, "pdf_result.html", context)

        return JsonResponse({"error": "No file uploaded."}, status=400)
    
    return render(request, "pdf.html")


tessdata_dir = r"C:\Program Files\Tesseract-OCR\tessdata"

# Get all .traineddata files in the folder and build lang string
traineddata_files = [f for f in os.listdir(tessdata_dir) if f.endswith('.traineddata')]
languages = '+'.join([os.path.splitext(f)[0] for f in traineddata_files])

def extract_text_from_pdf(pdf_file):
    """
    Extract text from an uploaded PDF file using PyPDF2's PdfReader.
    """
    extracted_text = ""
    try:
        images = convert_from_bytes(pdf_file.read())
        for page_num, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang=languages)
            extracted_text += f"\n--- Page {page_num + 1} ---\n{text}"
    except Exception as e:
        extracted_text = "Error extracting text: " + str(e)
        print("DEBUG: Exception during PDF extraction:", e)
    return extracted_text



def extract_text_from_image(image_file):
    """
    Extract text from an uploaded image file using Tesseract OCR.
    """
    extracted_text = ""
    try:
        image = Image.open(image_file)
        extracted_text = pytesseract.image_to_string(image, lang=languages)
    except Exception as e:
        extracted_text = "Error extracting text: " + str(e)
        print("DEBUG: Exception during image extraction:", e)
    return extracted_text


def extract_text_from_files(request):
    """
    Handle multiple uploaded PDFs/images, extract multi-language text using OCR.
    """
    if request.method == "POST":
        uploaded_files = request.FILES.getlist("files")
        all_text = ""
        print("DEBUG: request.method =", request.method)
        print("DEBUG: request.FILES =", request.FILES)
        print("DEBUG: uploaded_files length =", len(request.FILES.getlist("files")))

        user_id = request.session.get('user_id_after_login')
        if not user_id:
            return JsonResponse({"error": "User not logged in."}, status=400)
        user = User.objects.get(pk=user_id)

        for f in uploaded_files:
            filename = f.name.lower()
            if filename.endswith(".pdf"):
                text = extract_text_from_pdf(f)
            elif filename.endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff")):
                text = extract_text_from_image(f)
            else:
                text = f"Unsupported file type: {f.name}"

            # Create and save Invoice object for each file
            invoice = Invoice.objects.create(
                user=user,
                pdf_file=f,
                extracted_text=text
            )
            print(f"DEBUG: Created invoice with id {invoice.id} for user {user.id}")

            all_text += f"\n==== {f.name} ====\n{text}"

        # Optionally store in session for further processing
        request.session["extracted_text"] = all_text
        context = {
            "extracted_text": all_text
        }
        return render(request, "pdf_result.html", context)

    # For GET or other methods, just render the upload page or blank page
    return render(request, "pdf_result.html", {"extracted_text": ""})

def chat_invoice(request):
    """
    Accept a user's follow-up question about the invoice, use the extracted invoice text
    as context, call the Perplexity API, and update conversation history.
    """
    if request.method == "POST":
        user_question = request.POST.get("question")
        print("DEBUG: Received user question:", user_question)

        # Get the extracted text from the session
        extracted_text = request.session.get("extracted_text", "")
        if not extracted_text:
            print("DEBUG: No invoice text found in session.")
            return JsonResponse({"error": "No invoice data found. Please upload an invoice first."}, status=400)

        # Strong instructions to only answer questions related to the invoice
        system_content = (
            "You are an assistant specialized in analyzing invoices and financial documents written in multiple languages. "
            "You can understand and respond in English or in the same language as the invoice , whether it's English, Hindi, French, or others. "
            "You must only answer if the question is directly or indirectly related to the invoice content. "
            f"If the question is not related, respond exactly with: {DEFAULT_REJECTION}"
        )
        prompt = (
             "The following invoice content may be in any language.\n\n"
            f"Invoice details:\n{extracted_text}\n\n"
            f"User's question:\n{user_question}\n\n"
            "Respond accurately and in English or in the same language as the invoice text."
        )

        # Prepare the payload for the Perplexity API
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]

        # Get the logged-in user from the session
        user_id = request.session.get('user_id_after_login')
        user = User.objects.get(pk=user_id)

        # Get the most recent invoice of the user
        invoice = Invoice.objects.filter(user=user).last()

        # Define the API request and call the Perplexity API
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_content},
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            response = requests.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyDwiZBIVVyBaZrr6c5HtB4L8kr-EDRzOdE", json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                if answer.strip() == DEFAULT_REJECTION:
                    return JsonResponse({"error": "Please ask a question related to the invoice details."}, status=400)

                if invoice:
                    Conversation.objects.create(
                        invoice=invoice,
                        question=user_question,
                        answer=answer
                    )

                return JsonResponse({"answer": answer})
            else:
                return JsonResponse({"error": f"Gemini API error: {response.text}"}, status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": f"API error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)




def user_profile(request):
    user_id  = request.session.get('user_id_after_login')
    print(user_id)
    user = User.objects.get(pk= user_id)
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        try:
            profile = request.FILES['profile']
            user.photo = profile
        except MultiValueDictKeyError:
            profile = user.photo
        password = request.POST.get('password')
        location = request.POST.get('location')
        user.user_name = name
        user.email = email
        user.phone_number = phone
        user.password = password
        user.address = location
        user.save()
        messages.success(request , 'updated succesfully!')
        return redirect('user_profile')
    return render(request,'user-profile.html',{'user':user})



def history(request):
    user_id = request.session.get('user_id_after_login')
    if not user_id:
        return JsonResponse({"error": "User not logged in."}, status=400)
    user = User.objects.get(pk=user_id)
    invoices = Invoice.objects.filter(user=user).order_by('-date_uploaded')
    print(f"DEBUG: User {user.id} has {invoices.count()} invoices")
    history_data = []
    for invoice in invoices:
        conversations = Conversation.objects.filter(invoice=invoice)
        history_data.append({
            'invoice': invoice,
            'conversations': conversations
        })
    context = {
        "history_data": history_data
    }
    return render(request, "history.html", context)
