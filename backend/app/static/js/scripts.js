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


// fetch api
  async function loadAirports() {
    const response = await fetch('/api/airports'); // Gọi API để lấy danh sách sân bay
    const airports = await response.json();
    const from = document.querySelector(".find #from");
    const to = document.querySelector(".find #to");

    // Hàm để thêm danh sách sân bay vào dropdown
    function populateDropdown(selectElement, airports, exclude = null) {
        selectElement.innerHTML = '<option value="" disabled selected>Choose Airport</option>';
        airports.forEach(airport => {
            if (exclude !== airport.code) {
                const option = document.createElement('option');
                option.value = airport.id;
                option.textContent = `${airport.name} (${airport.code})`;
                selectElement.appendChild(option);
            }
        });
    }

    // Khởi tạo cả hai dropdown với tất cả sân bay
    populateDropdown(from, airports);
    populateDropdown(to, airports);

    // Lắng nghe sự thay đổi trong "from" và cập nhật "to"
    from.addEventListener('change', function () {
        const selectedCode = from.value;
        populateDropdown(to, airports, selectedCode); // Loại trừ sân bay được chọn
    });   
}

// Tải dữ liệu khi trang load
window.onload = loadAirports;


document.querySelectorAll('input[name="tripType"]').forEach(radio => {
  radio.addEventListener('change', function () {
      const returnInput = document.getElementById('return');
      if (this.value === 'oneway') {
          returnInput.disabled = true;
          returnInput.value = ""; // Reset giá trị
      } else {
          returnInput.disabled = false;
      }
  });
});


document.querySelector('.find button.btn').addEventListener('click', function () {
  const fromValue = document.querySelector('#from').value;
  const toValue = document.querySelector('#to').value;
  console.log(fromValue + ' ' + toValue);
  // SGN DAD
  if (fromValue && toValue) {
      // Gửi dữ liệu qua POST request
      fetch('/find_route', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            from: parseInt(fromValue, 10), // Ép kiểu thành số nguyên
            to: parseInt(toValue, 10)   
          })
      })
      .then(response => response.json())
      .then(data => {
          console.log(data);
          if (data.success) {
              alert(`Tìm thấy tuyến đường: ${data}`);

          } else {
              alert(`Không tìm thấy tuyến đường. Lý do: ${data.message}`);
          }
      })
      .catch(error => {
          console.error('Lỗi khi gửi yêu cầu:', error);
      });
  } else {
      alert('Vui lòng chọn cả "From" và "To".');
  }
});
