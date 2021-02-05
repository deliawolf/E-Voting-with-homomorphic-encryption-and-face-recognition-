from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic
from .models import Choice, Question, Voter, Pemilih
from phe import *
from django.views.generic import TemplateView
import pickle
import face_recognition
import cv2
import os
from django_user_agents.utils import get_user_agent

class Homepage(TemplateView):
    template_name = 'voting/homepage.html'

# Create your views here.
@method_decorator(login_required, name='dispatch')
class IndexView(generic.ListView):
    template_name = 'voting/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(status = 'p').order_by('-pub_date')


@method_decorator(login_required, name='dispatch')
class DetailView(generic.DetailView):
    model = Question
    template_name = 'voting/detail.html'
    #goal: Question.objects.filter(pub_date_end__gte=timezone.now())

    def get_queryset(self):
        return Question.objects.filter(pub_date_end__gte=timezone.now())


    #def get_queryset(self):
       # return redirect('voting/index.html',
                #        {
                     #       'question' : goal,
                      #      'error_massage_4': "Voting ditutup"
                      #  })

    #def render_to_response(self, context):
     #   if Question.objects.filter(pub_date_end__lt=timezone.now()):
      #      return redirect('voting:index')
    #    return super().render_to_response(context)

    #def get(self, request, *args, **kwargs):
     #   queryset = self.get_queryset()
      #  if Question.objects.get(pub_date_end__gte=timezone.now()):
       #     return redirect('voting:index')
        #else:
         #   return redirect('voting:detail')
        #return super.get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class ResultsView(generic.DetailView, Question):
    model = Question
    template_name = 'voting/results.html'

    def get_queryset(self):
       return Question.objects.filter(pub_date_end__lte=timezone.now())

def vote(request, question_id):

        user = request.user
        question = get_object_or_404(Question, pk=question_id)

        try:
            selected_choice = question.choice_set.get(pk=request.POST['choice'])
        except(KeyError, Choice.DoesNotExist):
            #menampilkan form pertanyaan
            return render(request, 'voting/detail.html',
            {
                'question': question,
                'error_massage': "Anda tidak memilih"
            })
        if Voter.objects.filter(question=question, user=request.user).exists():
            return render(request, 'voting/detail.html',
                {
                    'question': question,
                    'error_massage': "Anda telah memilih Sebelumnya",
                    'error_massage_2': "Pengingat : Hasil hanya bisa dibuka setelah Voting ditutup"

                })
        #currentTime = datetime.datetime.now()
        #if Question.objects.filter(pub_date_end__lte=currentTime).exists():
         #   return render(request, 'voting/detail.html',
          #      {
           #         'question': question,
            ##       'error_massage_2': "Pengingat : Hasil hanya dapat dibuka setelah voting ditutup"
              #  })
        else:
             Voter.objects.update_or_create(
                user=user,
                question=question,
             )
             if selected_choice.votes == 0:

                 public_key, private_key = paillier.generate_paillier_keypair()

                 list_public_key = []
                 list_private_key = []
                 list_enkripsi = []

                 enkripsi_votes = public_key.encrypt(selected_choice.votes)
                 enkripsi_votes = enkripsi_votes + 1

                 list_public_key.append(public_key)
                 list_private_key.append(private_key)
                 list_enkripsi.append(enkripsi_votes)
                 list_enkripsi.append(enkripsi_votes.ciphertext())


                 pickle_list_public_key = pickle.dumps(list_public_key)
                 pickle_list_private_key = pickle.dumps(list_private_key)
                 pickle_list_enkripsi = pickle.dumps(list_enkripsi)


                 selected_choice.kunci_publik = pickle_list_public_key
                 selected_choice.kunci_privat = pickle_list_private_key
                 selected_choice.enkripsi = pickle_list_enkripsi
                 selected_choice.enkripsi_stats = "Yes"

             elif selected_choice.votes > 0:

                  list_enkripsi = pickle.loads(selected_choice.enkripsi)
                  enkripsi_votes = list_enkripsi.pop(0)
                  list_enkripsi.pop(0)

                  enkripsi_votes = enkripsi_votes + 1

                  list_enkripsi.append(enkripsi_votes)
                  list_enkripsi.append(enkripsi_votes.ciphertext())

                  pickle_list_enkripsi = pickle.dumps(list_enkripsi)

                  selected_choice.enkripsi = pickle_list_enkripsi

             #list_enkripsi_for_dekripsi = pickle.loads(selected_choice.enkripsi)
             #enkripsi_for_dekripsi = list_enkripsi_for_dekripsi.pop(0)
             #list_enkripsi_for_dekripsi.pop(0)


             #list_private_key_for_dekripsi = pickle.loads(selected_choice.kunci_privat)
             #private_key = list_private_key_for_dekripsi.pop(0)

             #dekripsi = private_key.decrypt(enkripsi_for_dekripsi)

             #selected_choice.votes = dekripsi

             selected_choice.save()

             return render(request, 'voting/detail.html',
                          {
                             'question': question,
                              'error_massage' : "Selamat anda berhasil melakukan voting",
                              'error_massage_2': "Pengingat : Hasil voting daapt dilihat dan diakses setelah proses voting keseluruhan berakhir"
                          })

def dekripsivote(request, question_id):

    user = request.user
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except(KeyError, Choice.DoesNotExist):
        # menampilkan form pertanyaan
        return render(request, 'voting/dekripsi.html',
                      {
                          'question': question,
                          'error_massage': "Anda tidak memilih"
                      })
    if selected_choice.enkripsi_stats == 'No':

        return render(request, 'voting/dekripsi.html',
                      {
                          'question': question,
                          'error_massage': "Nilai belum dienkripsi, tidak bisa didekripsi",
                      })
    else:
        list_enkripsi_for_dekripsi = pickle.loads(selected_choice.enkripsi)
        enkripsi_for_dekripsi = list_enkripsi_for_dekripsi.pop(0)
        list_enkripsi_for_dekripsi.pop(0)

        list_private_key_for_dekripsi = pickle.loads(selected_choice.kunci_privat)
        private_key = list_private_key_for_dekripsi.pop(0)

        dekripsi = private_key.decrypt(enkripsi_for_dekripsi)

        selected_choice.votes = dekripsi

        selected_choice.save()

        return render(request, 'voting/dekripsi.html',
                      {
                          'question': question,
                          'error_massage': "Selamat anda berhasil melakukan dekripsi",
                      })

#def registerpage(request):
    #if request.user.is_authenticated:
     #   return redirect('voting:index')
    #else:
     #form = UserCreationForm()
     #if request.method == 'POST':
      #  form = UserCreationForm(request.POST)
       # if form.is_valid():
        #    user = form.save()
         #   group = Group.objects.get_by_natural_key('Pemilih',)
          #  user.groups.add(group)
           # form.cleaned_data.get('username')
            #messages.success(request, 'Account was created' )
            #return redirect('voting:login')

     #context = {'form': form}
     #return render(request, 'voting/register.html', context)

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('voting:index')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                try:
                    if user.pemilih.head_shot_status_pass == True:
                        login(request, user)
                        return redirect('voting:index')
                    elif facedect(user.pemilih.head_shot.url):
                        login(request, user)
                        return redirect('voting:index')
                    else:
                        messages.info(request, 'Foto tidak jelas, coba kembali')
                except ObjectDoesNotExist:
                    messages.info(request,'Anda Tidak memiliki Foto, Coba Hubungi Petugas')
                except ValueError:
                    messages.info(request,'Posisikan wajah menghadap kamera, Foto tidak jelas, coba kembali')
            else:
                messages.info(request, 'Username/NIK atau password salah')
                messages.info(request, 'Foto Anda tidak sesuai dengan Foto data KPU')
    context = {}
    return render(request, 'voting/login.html', context)


def logoutuser(request):
    logout(request)
    return redirect('voting:login')

def facedect(loc, request):
    user_agent = get_user_agent(Request)
    if user_agent.is_mobile:
        cam = cv2.VideoCapture(1)
    elif user_agent.is_tablet:
        cam = cv2.VideoCapture(1)
    else:
        cam = cv2.VideoCapture(0)
        s, img = cam.read()
        if s:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            MEDIA_ROOT = os.path.join(BASE_DIR, '')
            loc = (str(MEDIA_ROOT) + loc)
            face_1_image = face_recognition.load_image_file(loc)
            face_1_face_encoding = face_recognition.face_encodings(face_1_image)[0]

            small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            check = face_recognition.compare_faces(face_1_face_encoding, face_encodings)

            print(check)
            if check[0]:
                return True
            else:
                return False
            messages.info(request, 'Foto tidak jelas, coba kembali')

    cam.release()
    cv2.destroyAllWindows()

def common(request):
    return render(request, 'voting/common.html')

def commonhomepage(request):
    return render(request, 'voting/common_homepage.html')

def error_404_view(request, exception):
    data = {"name": "ThePythonDjango.com"}
    return render(request,'voting/404.html', data)


