# sitio_web/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages  # <-- Para mensajes de éxito / error

from .models import (
    Profile,
    Project,
    ProjectAssignment,
    ProjectUpdate,
    Document,
    Message,
)
from .forms import ProjectUpdateForm, MessageForm, MessageReplyForm, DocumentForm

def home(request):
    """
    Página de inicio pública del sitio.
    """
    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Inicio',
    }
    return render(request, 'sitio_web/home.html', context)


def custom_login(request):
    """
    Vista de inicio de sesión para todos los usuarios (admin, trabajador, cliente).
    Después de iniciar sesión, serán redirigidos al dashboard, que hará la lógica
    según el rol.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = "Usuario o contraseña incorrectos."

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Iniciar sesión',
        'error_message': error_message,
    }
    return render(request, 'sitio_web/login.html', context)


def custom_logout(request):
    """
    Cierra la sesión del usuario y lo redirige a la página de inicio.
    """
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    """
    Vista principal después de iniciar sesión.
    Según el rol del usuario (Profile.role), mostramos distinta información.
    """
    profile = getattr(request.user, 'profile', None)
    role = profile.role if profile else 'CLIENT'

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Panel de usuario',
        'role': role,
    }

    if role == 'ADMIN':
        projects = Project.objects.all().order_by('-created_at')[:10]
        context['projects'] = projects
        template_name = 'sitio_web/dashboard_admin.html'

    elif role == 'WORKER':
        assignments = ProjectAssignment.objects.filter(
            worker=request.user
        ).select_related('project')
        projects = [assignment.project for assignment in assignments]
        context['projects'] = projects
        template_name = 'sitio_web/dashboard_worker.html'

    else:
        projects = Project.objects.filter(client=request.user).order_by('-created_at')
        context['projects'] = projects
        template_name = 'sitio_web/dashboard_client.html'

    return render(request, template_name, context)


@login_required
def worker_project_detail(request, project_id):
    """
    Detalle de un proyecto visto por un trabajador.
    Solo accesible si el proyecto está asignado a ese trabajador.
    Muestra información básica y el historial de actualizaciones.
    """
    project = get_object_or_404(Project, id=project_id)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'WORKER':
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")

    is_assigned = ProjectAssignment.objects.filter(
        project=project,
        worker=request.user
    ).exists()

    if not is_assigned:
        return HttpResponseForbidden("No estás asignado a este proyecto.")

    updates = ProjectUpdate.objects.filter(project=project).order_by('-date')

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Detalle proyecto (Trabajador)',
        'project': project,
        'updates': updates,
    }
    return render(request, 'sitio_web/worker_project_detail.html', context)


@login_required
def worker_add_update(request, project_id):
    """
    Permite al trabajador agregar una nueva actualización de avance
    para un proyecto asignado.
    """
    project = get_object_or_404(Project, id=project_id)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'WORKER':
        return HttpResponseForbidden("No tienes permiso para actualizar este proyecto.")

    is_assigned = ProjectAssignment.objects.filter(
        project=project,
        worker=request.user
    ).exists()

    if not is_assigned:
        return HttpResponseForbidden("No estás asignado a este proyecto.")

    if request.method == 'POST':
        form = ProjectUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            update = form.save(commit=False)
            update.project = project
            update.author = request.user
            update.save()

            # Actualizar el porcentaje de avance del proyecto
            project.progress_percent = update.progress_percent
            project.save(update_fields=['progress_percent'])

            # MENSAJE DE ÉXITO
            messages.success(
                request,
                f'Avance registrado exitosamente para "{project.name}" ({{}}%).'.format(update.progress_percent)
            )

            return redirect('worker_project_detail', project_id=project.id)
    else:
        form = ProjectUpdateForm(initial={'progress_percent': project.progress_percent})

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Registrar avance',
        'project': project,
        'form': form,
    }
    return render(request, 'sitio_web/worker_add_update.html', context)


@login_required
def client_project_detail(request, project_id):
    """
    Detalle de un proyecto visto por un cliente.
    Solo accesible si el proyecto pertenece a ese cliente.
    Muestra información básica, el historial de actualizaciones y documentos visibles.
    """
    project = get_object_or_404(Project, id=project_id)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'CLIENT' or project.client != request.user:
        return HttpResponseForbidden("No tienes permiso para acceder a este proyecto.")

    updates = ProjectUpdate.objects.filter(project=project).order_by('-date')
    documents = Document.objects.filter(
        project=project,
        visible_to_client=True
    ).order_by('-uploaded_at')

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Detalle proyecto (Cliente)',
        'project': project,
        'updates': updates,
        'documents': documents,
    }
    return render(request, 'sitio_web/client_project_detail.html', context)


@login_required
def client_send_message(request, project_id):
    """
    Permite al CLIENTE enviar un mensaje asociado a uno de sus proyectos.
    El mensaje va dirigido al equipo administrativo (receiver = None).
    """
    project = get_object_or_404(Project, id=project_id)

    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'CLIENT' or project.client != request.user:
        return HttpResponseForbidden("No tienes permiso para enviar mensajes sobre este proyecto.")

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.project = project
            msg.sender = request.user
            msg.receiver = None
            msg.save()

            # MENSAJE DE ÉXITO
            messages.success(
                request,
                'Mensaje enviado exitosamente. Recibirás una respuesta pronto.'
            )

            return redirect('client_project_detail', project_id=project.id)
    else:
        form = MessageForm()

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Enviar mensaje',
        'project': project,
        'form': form,
    }
    return render(request, 'sitio_web/client_send_message.html', context)


@login_required
def client_inbox(request):
    """
    Bandeja de entrada para CLIENTES.
    Muestra los mensajes enviados por el staff al cliente y los mensajes enviados por el cliente.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role != 'CLIENT':
        return HttpResponseForbidden("No tienes permiso para ver esta bandeja de entrada.")

    # Mensajes donde el cliente es el receptor (respuestas del staff)
    messages_to_client = Message.objects.filter(
        receiver=request.user
    ).select_related('sender', 'project').order_by('-sent_at')

    # Mensajes enviados por el cliente
    messages_from_client = Message.objects.filter(
        sender=request.user
    ).select_related('receiver', 'project').order_by('-sent_at')

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Mi bandeja de mensajes',
        'messages_to_client': messages_to_client,
        'messages_from_client': messages_from_client,
    }
    return render(request, 'sitio_web/client_inbox.html', context)


@login_required
def staff_inbox(request):
    """
    Bandeja de entrada para ADMIN y WORKER.
    Muestra todos los mensajes enviados por clientes,
    opcionalmente filtrados por proyecto.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in ['ADMIN', 'WORKER']:
        return HttpResponseForbidden("No tienes permiso para ver los mensajes.")

    messages_qs = Message.objects.filter(
        sender__profile__role='CLIENT'
    ).select_related('sender', 'project').order_by('-sent_at')

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Bandeja de mensajes',
        'messages': messages_qs,
    }
    return render(request, 'sitio_web/staff_inbox.html', context)


@login_required
def staff_reply_message(request, message_id):
    """
    Permite a ADMIN o WORKER responder un mensaje enviado por un cliente.
    Crea un nuevo Message donde el sender es el usuario staff y el receiver es el cliente.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in ['ADMIN', 'WORKER']:
        return HttpResponseForbidden("No tienes permiso para responder mensajes.")

    original_message = get_object_or_404(
        Message.objects.select_related('sender', 'project'),
        id=message_id
    )

    # Solo se responde a mensajes cuyo remitente es un CLIENTE
    sender_profile = getattr(original_message.sender, 'profile', None)
    if not sender_profile or sender_profile.role != 'CLIENT':
        return HttpResponseForbidden("Solo se pueden responder mensajes enviados por clientes.")

    if request.method == 'POST':
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.project = original_message.project
            reply.sender = request.user
            reply.receiver = original_message.sender
            reply.subject = f"Re: {original_message.subject}"
            reply.save()

            # MENSAJE DE ÉXITO
            messages.success(
                request,
                f'Respuesta enviada exitosamente a {original_message.sender.username}.'
            )

            return redirect('staff_inbox')
    else:
        form = MessageReplyForm()

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': 'Responder mensaje',
        'original_message': original_message,
        'form': form,
    }
    return render(request, 'sitio_web/staff_reply_message.html', context)

# -------------------------------------------------------------
#  Gestión de documentos de proyecto por parte del staff
# -------------------------------------------------------------

@login_required
def staff_project_documents(request, project_id):
    """
    Vista para que ADMIN y WORKER vean los documentos de un proyecto
    y accedan a la subida de nuevos documentos.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in ['ADMIN', 'WORKER']:
        return HttpResponseForbidden("No tienes permiso para ver los documentos de este proyecto.")

    project = get_object_or_404(Project, id=project_id)
    documents = Document.objects.filter(project=project).order_by('-uploaded_at')

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': f'Documentos del proyecto: {project.name}',
        'project': project,
        'documents': documents,
    }
    return render(request, 'sitio_web/staff_project_documents.html', context)


@login_required
def staff_upload_document(request, project_id):
    """
    Permite a ADMIN o WORKER subir un nuevo documento para un proyecto.
    """
    profile = getattr(request.user, 'profile', None)
    if not profile or profile.role not in ['ADMIN', 'WORKER']:
        return HttpResponseForbidden("No tienes permiso para subir documentos para este proyecto.")

    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.project = project
            doc.uploaded_by = request.user
            doc.save()

            messages.success(request, f'Documento "{doc.title}" subido correctamente.')
            return redirect('staff_project_documents', project_id=project.id)
    else:
        form = DocumentForm()

    context = {
        'company_name': 'CCR CONSULTORES',
        'page_title': f'Subir documento para: {project.name}',
        'project': project,
        'form': form,
    }
    return render(request, 'sitio_web/staff_upload_document.html', context)