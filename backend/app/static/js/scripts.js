// JavaScript scripts
window.addEventListener("scroll", function () {
  const navbar = document.querySelector(".navbar-home");
  // Kiểm tra nếu đang ở trang chủ
  if (window.location.pathname === "/") {
    if (window.scrollY > navbar.clientHeight) {
      navbar.classList.add("fixed", "bg-white"); // Áp dụng class fixed
      navbar.classList.remove("rounded-2");
      navbar.classList.remove("not-fixed"); // Loại bỏ class not-fixed
    } else {
      navbar.classList.add("not-fixed"); // Áp dụng class not-fixed
      navbar.classList.remove("fixed", "bg-white"); // Loại bỏ class fixed
      navbar.classList.add("rounded-2");
    }
  } else {
    navbar.classList.add("fixed", "bg-white"); // Navbar cố định cho các trang khác
    navbar.classList.remove("fixed"); // Loại bỏ class fixed
    navbar.classList.remove("not-fixed");
  }
});

const navbar = document.querySelector(".navbar-home");
console.log(navbar.clientHeight);

navbar_toggle_btn = navbar.querySelector(".navbar-toggler");
navbar_toggle_btn.addEventListener("click", function () {
  if (
    navbar_toggle_btn.getAttribute("aria-expanded") === "false" &&
    window.scrollY < navbar.clientHeight
  ) {
    navbar.classList.remove("bg-white");
  } else {
    navbar.classList.add("bg-white");
  }
});

document.addEventListener("DOMContentLoaded", function () {
  const swiper = new Swiper(".swiper-container", {
    loop: true,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    autoplay: {
      delay: 2000,
      disableOnInteraction: false,
    },
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const swiper = new Swiper(".swiper", {
    loop: true,
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    autoplay: {
      delay: 2000,
      disableOnInteraction: false,
    },
  });
});

const counters = document.querySelectorAll(".count");
counters.forEach((counter) => {
  const target = +counter.getAttribute("data-target");
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


// animation
document.addEventListener("DOMContentLoaded", () => {
  const fadeElements = document.querySelectorAll(
      ".fade-left, .fade-right, .fade-opacity, .fade-translate"
  );

  const handleScroll = () => {
      fadeElements.forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.top < window.innerHeight && rect.bottom > 0) {
              el.classList.add("visible"); // Thêm class 'visible' khi phần tử vào viewport
          }
      });
  };

  window.addEventListener("scroll", handleScroll);
  handleScroll(); // Kích hoạt lần đầu khi load trang
});

// end animation