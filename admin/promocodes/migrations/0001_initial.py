# Generated by Django 4.1.7 on 2024-07-27 00:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='Промокод')),
                ('discount', models.FloatField(default=0, verbose_name='Размер скидки')),
                ('discount_type', models.CharField(choices=[('fixed', 'Fixed'), ('percentage', 'Percentage'), ('trial', 'Trial')], default='fixed', max_length=15, verbose_name='Тип скидки')),
                ('num_uses', models.PositiveIntegerField(default=1, verbose_name='Доступное количество использований')),
                ('is_active', models.BooleanField(default=True, verbose_name='Действителен')),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
                ('expiration_date', models.DateField(blank=True, default=None, null=True, verbose_name='Срок действия')),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Промокод',
                'verbose_name_plural': 'Промокоды',
                'db_table': 'promo_codes',
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название')),
                ('price', models.FloatField(verbose_name='Стоимость')),
                ('description', models.CharField(max_length=255, verbose_name='Описание')),
                ('is_deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Тариф',
                'verbose_name_plural': 'Тарифы',
                'db_table': 'tariffs',
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.FloatField(verbose_name='Итоговая стоимость')),
                ('purchase_date', models.DateField(auto_now_add=True, verbose_name='Дата покупки')),
                ('promo_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='promocodes.promocode')),
                ('tariff', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='promocodes.tariff', verbose_name='Тариф')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Покупка',
                'verbose_name_plural': 'Покупки',
                'db_table': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='AvailableForUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ManyToManyField(blank=True, to='users.group', verbose_name='Группа пользователей')),
                ('promo_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='promocodes.promocode', verbose_name='Промокод')),
                ('user', models.ManyToManyField(blank=True, to='users.user', verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Доступ',
                'verbose_name_plural': 'Доступы',
                'db_table': 'availables',
            },
        ),
    ]
