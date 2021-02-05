import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
STATUS_CHOICES = [
    ('d', 'draft'),
    ('p', 'published')
]
class Question(models.Model):
    question_text = models.CharField(max_length=200, verbose_name="Judul Pemungutan Suara")
    pub_date = models.DateTimeField('data di publish')
    pub_date_end = models.DateTimeField('data ditutup')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d')


    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
        if now >= pub_date_end: Question.objects.exclude(status="withdrawn")
        was_published_recently.admin_order_field = 'pub_date'
        was_published_recently.boolean = true
        was_published_recently.short_description = 'published recently?'

    class Meta:
        verbose_name = "Pemungutan Suara"
        verbose_name_plural = "Pemungutan Suara"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField('calon pilihan', max_length=35)
    choice_text2 = models.CharField('Wakil Calon Pilihan', max_length=35, default='')
    enkripsi = models.BinaryField(default=None, null=True)
    kunci_publik = models.BinaryField(default=None, null=True)
    kunci_privat = models.BinaryField(default=None, null=True)
    enkripsi_stats = models.CharField(max_length=100, default='No')
    votes = models.IntegerField('jumlah', default=0, db_column='votes')
    image = models.ImageField(upload_to='post_image')

    def __str__(self):
        return self.choice_text

    class Meta:
        verbose_name = "Pilihan"
        verbose_name_plural = "Pilihan"

class Pemilih(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    head_shot = models.ImageField(upload_to='profil_images', help_text="Gambar wajah yang digunakan untuk validasi masuk sistem pemungutan suara", verbose_name='Foto Wajah')
    is_pemilih = models.BooleanField(default=False, help_text="Menentukan apakah pengguna merupakan kategori pemilih atau tidak", verbose_name='Pemilih')
    head_shot_status_pass = models.BooleanField(default=False, help_text="Menentukan apakah pengguna dapat masuk tanpa validasi wajah", verbose_name="lewati validasi wajah")
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Pemilih"
        verbose_name_plural = "Pemilih"

class Voter(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = (
            ('question', 'user'),
        )

