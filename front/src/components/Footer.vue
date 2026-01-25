<!-- src/components/Footer.vue -->
<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-column">
        <h4 class="footer-column-title">О сервисе</h4>
        <ul class="footer-links">
          <li><a href="#" class="footer-link">О сервисе</a></li>
          <li><a href="#" class="footer-link">Как это работает</a></li>
          <li><a href="#" class="footer-link">Курсы</a></li>
          <li><a href="#" class="footer-link">О преподавателе</a></li>
        </ul>
      </div>
      <div class="footer-column">
        <h4 class="footer-column-title">Информация</h4>
        <ul class="footer-links">
          <li><a href="#" class="footer-link">Переговоров индивидуальности</a></li>
          <li><a href="#" class="footer-link">Пользовательское соглашение</a></li>
        </ul>
      </div>
      <div class="footer-column">
        <h4 class="footer-column-title">Контакты</h4>
        <ul class="footer-links">
          <li>
            <a href="#" class="footer-link">
              <span class="footer-link-icon">@</span>
              flare_school
            </a>
          </li>
          <li>
            <a href="#" class="footer-link">
              <span class="footer-link-icon">✉</span>
              manager-01@gmail.com
            </a>
          </li>
        </ul>
      </div>
      <div class="footer-column">
        <h4 class="footer-column-title">F.L.A.R.E.</h4>
        <p class="footer-description">
          Переделываем образовательный курс и адаптируем обучение и урок занятий. Самое преподовательство — некз...
        </p>
      </div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copyright">
        <span>© 2008 / F.L.A.R.E. Все права защищены.</span>
      </div>
      <div class="footer-legal">
        <a href="#" class="footer-link">Политика конфиденциальности</a>
        <span class="footer-separator">—</span>
        <a href="#" class="footer-link">Куки</a>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Компонент футера
</script>

<style scoped>
.footer {
  background: rgba(20, 20, 20, 0.95);
  padding: 60px 32px 30px;
  margin-top: 60px;
  box-sizing: border-box;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 40px;
  margin-bottom: 40px;
  box-sizing: border-box;
}

.footer-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.footer-column-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
  padding: 0;
  color: #FFFFFF;
}

.footer-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.footer-link:hover {
  color: #FFD700;
}

.footer-link-icon {
  font-size: 1rem;
}

.footer-description {
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin: 0;
  padding: 0;
}

.footer-bottom {
  max-width: 1400px;
  margin: 0 auto;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  box-sizing: border-box;
}

.footer-copyright {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.footer-legal {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

.footer-separator {
  color: rgba(255, 255, 255, 0.5);
}

/* Адаптивность */
@media (max-width: 1200px) {
  .footer-content {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .footer {
    padding: 50px 20px 25px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 30px;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .footer {
    padding: 40px 16px 20px;
  }
}
</style>