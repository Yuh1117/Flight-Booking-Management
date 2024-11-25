// JavaScript scripts
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar-home');
    
    if (window.scrollY > 50) {
      navbar.style.position = 'fixed';
      navbar.style.top = '0';
      navbar.style.left = '0';
      navbar.style.right = '0';
      navbar.classList.remove('rounded-4'); // Bỏ class rounded
    } else {
      navbar.style.position = 'absolute';
      navbar.style.top = '30px';
      navbar.style.left = '20px';
      navbar.style.right = '20px';
      navbar.classList.add('rounded-4'); 
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