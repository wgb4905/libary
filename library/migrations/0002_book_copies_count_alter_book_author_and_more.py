# Generated by Django 4.2.20 on 2025-04-04 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='copies_count',
            field=models.PositiveIntegerField(default=1, help_text='保存时将自动创建指定数量的副本', verbose_name='副本数量'),
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=100, verbose_name='作者'),
        ),
        migrations.AlterField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='book_covers/', verbose_name='封面'),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(verbose_name='简介'),
        ),
        migrations.AlterField(
            model_name='book',
            name='keywords',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='关键字'),
        ),
        migrations.AlterField(
            model_name='book',
            name='recommended_age',
            field=models.IntegerField(blank=True, null=True, verbose_name='推荐年龄'),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=100, verbose_name='书名'),
        ),
        migrations.AlterField(
            model_name='bookimage',
            name='caption',
            field=models.CharField(blank=True, max_length=200, verbose_name='图片备注'),
        ),
        migrations.AlterField(
            model_name='bookimage',
            name='image',
            field=models.ImageField(upload_to='book_gallery/', verbose_name='详情轮播图片'),
        ),
    ]
