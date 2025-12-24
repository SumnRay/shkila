# Инструкции по деплою

## Деплой фронтенда через GitHub

### Первоначальная настройка на сервере (один раз):

1. **Клонировать репозиторий на сервер** (если еще не клонирован):
   ```bash
   cd /var/www
   sudo git clone https://github.com/SumnRay/shkila.git
   sudo chown -R $USER:$USER /var/www/shkila
   ```

2. **Установить Node.js и npm** (если еще не установлены):
   ```bash
   # Для Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

3. **Убедиться что на правильной ветке (alpha3)**:
   ```bash
   cd /var/www/shkila
   git checkout alpha3
   git pull origin alpha3
   ```

4. **Установить зависимости фронтенда**:
   ```bash
   cd /var/www/shkila/front
   npm install
   ```

5. **Настроить git для правильной работы pull**:
   ```bash
   cd /var/www/shkila
   git config pull.rebase false
   ```

### Обновление фронтенда (каждый раз):

**Локально:**
```bash
git add .
git commit -m "Описание изменений"
git push origin main
```

**На сервере:**
```bash
/var/www/shkila/deploy/deploy_frontend.sh
```

Или вручную:
```bash
cd /var/www/shkila
git pull origin alpha3
cd front
npm install  # только если добавились новые зависимости
npm run build
sudo cp -r dist/* /var/www/frontend/
sudo chown -R www-data:www-data /var/www/frontend
sudo chmod -R 755 /var/www/frontend
```

### Важные замечания:

- ⚠️ Убедись что на сервере установлен Node.js версии 18+ и npm
- ⚠️ Путь к проекту должен быть `/var/www/shkila` (или измени скрипт под свой путь)
- ⚠️ Для работы `git pull` на сервере может понадобиться настроить SSH ключи или использовать HTTPS с кэшем пароля
- ⚠️ После обновления проверь сайт в браузере (может понадобиться очистить кэш: Ctrl+Shift+R)

### Если git pull требует пароль:

**Вариант 1: Использовать SSH ключи (рекомендуется)**
```bash
# На сервере сгенерировать SSH ключ
ssh-keygen -t ed25519 -C "server@flare-school"

# Добавить публичный ключ в GitHub (Settings → SSH and GPG keys → New SSH key)
cat ~/.ssh/id_ed25519.pub

# Изменить remote на SSH URL
cd /var/www/shkila
git remote set-url origin git@github.com:SumnRay/shkila.git
```

**Вариант 2: Использовать Personal Access Token**
```bash
# В GitHub: Settings → Developer settings → Personal access tokens → Generate new token
# Скопировать токен

# При git pull использовать токен вместо пароля
# Или настроить кэш:
git config --global credential.helper store
```

