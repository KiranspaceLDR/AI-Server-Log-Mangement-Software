# Error_log/views.py

import os
import webbrowser
import subprocess
from googlesearch import search
from .ml_model import predict_threat_level,Error_Extraction
from django.db.models import Count
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import FileUpload 

def home(request):
    return render(request, 'home.html')


def protected_view(request):
    return render(request, 'protected_view.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
@login_required
def upload_file_view(request):
    return render(request, 'upload_file.html')

def dashboard(request):
    # Query the database for required information
    error_counts = FileUpload.objects.values('threat_level').annotate(count=Count('id'))
    upload_counts = FileUpload.objects.values('upload_date').annotate(count=Count('id'))
    extracted_error_counts = FileUpload.objects.values('error_message').annotate(count=Count('id'))

    # Convert the querysets to JSON for chart rendering
    
    error_counts_json = json.dumps(list(error_counts), indent=4, default=str)
    upload_counts_json = json.dumps(list(upload_counts), indent=4, default=str)
    extracted_error_counts_json = json.dumps(list(extracted_error_counts), indent=4, default=str)

    return render(request, 'dashboard.html', {'error_counts': error_counts_json, 'upload_counts': upload_counts_json})

def compile_and_search(request):
    response = None

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        try:
            if uploaded_file:
                # Save the uploaded file
                file_name, file_extension = os.path.splitext(uploaded_file.name)
                language = file_extension[1:]  # Exclude the dot in the extension

                with open(f'Error_log/uploaded_file.{language}', 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                # Attempt to compile the uploaded file based on the specified language
                if language == 'py':
                    result = subprocess.run(['python', '-m', 'py_compile', f'Error_log/uploaded_file.{language}'], capture_output=True)
                    request.session['python_response'] = result.stderr.decode('utf-8') if result.returncode != 0 else None
                elif language == 'java':
                    result = subprocess.run(['javac', f'Error_log/uploaded_file.{language}'], capture_output=True)
                    request.session['java_response'] = result.stderr.decode('utf-8') if result.returncode != 0 else None

                if result.returncode == 0:
                    # If compilation succeeds, there are no syntax errors
                    response = f"File compiled successfully. No syntax errors found for {language.capitalize()}."
                    if language=='py':
                        FileUpload.objects.create(error_count=0, threat_level='', error_message='')
                    # Clear previous responses for other languages
                    request.session['python_response'] = None
                    request.session['java_response'] = None

                else:
                    if language=='py':
                    # If compilation fails, extract the error
                        compilation_error = result.stderr.decode('utf-8')
                        response = f"Compilation error for {language.capitalize()}:\n\n{compilation_error}"
                        threat_level = predict_threat_level(compilation_error)
                        extracted_error = Error_Extraction(compilation_error)
                    
                        error_count = FileUpload.objects.filter(threat_level='').count() + 1
                        FileUpload.objects.create(error_count=error_count, threat_level=threat_level, error_message=extracted_error)
                        response += f"\n\nPredicted Threat Level: {threat_level}"
                    else:
                        compilation_error = result.stderr.decode('utf-8')
                        error_lines = compilation_error.strip().split('^')
                        response = f"Compilation error for {language.capitalize()}:\n"
                        for i, error_line in enumerate(error_lines, start=1):
                            response += f"{i}.{error_line.strip()}\n"
                    # Search for the error message on Google
                    search_query = f"{language.capitalize()} compilation error: {compilation_error}"
                    google_results = list(search(search_query, num=5, stop=5, pause=2))
                    if google_results and language=='java':
                                google_search_url = f"https://www.google.com/search?q={'+'.join(search_query.split())}"
                                webbrowser.open_new_tab(google_search_url)
                    # Open a maximum of 2 tabs
                    else:
                        max_tabs = 2
                        for i, result in enumerate(google_results):
                            if i >= max_tabs:
                                break
                            webbrowser.open_new_tab(result)

            else:
                response = "No file uploaded."

        except Exception as e:
            # Handle other exceptions
            response = f"Error: {str(e)}"
    
    

    return render(request, 'Error_log/upload_file.html', {'response': response})
    