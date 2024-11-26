// JavaScript scripts
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar-home');
  // Kiểm tra nếu đang ở trang chủ
  if (window.location.pathname === '/') {
    if (window.scrollY > 50) {
      navbar.classList.add('fixed'); // Áp dụng class fixed
      navbar.classList.remove('rounded-4');
      navbar.classList.remove('not-fixed'); // Loại bỏ class not-fixed
    } else {
      navbar.classList.add('not-fixed'); // Áp dụng class not-fixed
      navbar.classList.remove('fixed'); // Loại bỏ class fixed
      navbar.classList.add('rounded-4'); 
      
    }
  } else {
    navbar.classList.add('fixed'); // Navbar cố định cho các trang khác
    navbar.classList.remove('fixed'); // Loại bỏ class fixed
    navbar.classList.remove('not-fixed');
  }
});



  document.addEventListener('DOMContentLoaded', function () {
    const swiper = new Swiper('.swiper-container', {
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        autoplay: {
            delay: 2000,
            disableOnInteraction: false,
        },
    });
});


document.addEventListener("DOMContentLoaded", () => {
  const swiper = new Swiper('.swiper', {
    loop: true,
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    autoplay: {
        delay: 2000,
        disableOnInteraction: false,
    },
  });
});


const counters = document.querySelectorAll('.count');
  counters.forEach(counter => {
    const target = +counter.getAttribute('data-target');
    let current = 0;
    const increment = target / 100;

    const updateCounter = () => {
      current += increment;
      if (current >= target) {
        counter.textContent = target;
        clearInterval(interval);
      } else {
        counter.textContent = Math.floor(current);
      }
    };

    const interval = setInterval(updateCounter, 50);
  });