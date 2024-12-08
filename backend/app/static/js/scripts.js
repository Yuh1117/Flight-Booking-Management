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
  const response = await fetch("/api/airports"); // Gọi API để lấy danh sách sân bay
  const airports = await response.json();
  const from = document.querySelector(".find #from");
  const to = document.querySelector(".find #to");

  // Hàm để thêm danh sách sân bay vào dropdown
  function populateDropdown(selectElement, airports, exclude = null) {
    selectElement.innerHTML =
      '<option value="" disabled selected>Choose Airport</option>';
    airports.forEach((airport) => {
      if (exclude !== airport.code) {
        const option = document.createElement("option");
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
  from.addEventListener("change", function () {
    const selectedCode = from.value;
    populateDropdown(to, airports, selectedCode); // Loại trừ sân bay được chọn
  });
}

// Tải dữ liệu khi trang load
// window.onload = loadAirports;

document.querySelectorAll('input[name="tripType"]').forEach((radio) => {
  radio.addEventListener("change", function () {
    const returnInput = document.getElementById("return");
    if (this.value === "oneway") {
      returnInput.disabled = true;
      returnInput.value = ""; // Reset giá trị
    } else {
      returnInput.disabled = false;
    }
  });
});

// document
//   .querySelector(".find button.btn")
//   .addEventListener("click", function () {
    
//     const fromValue = document.querySelector("#from").value;
//     const toValue = document.querySelector("#to").value;
//     const departDateInput = document.getElementById("depart").value;
//     console.log(fromValue + " " + toValue);
//     // SGN DAD
//     if (fromValue && toValue) {
//       // Gửi dữ liệu qua POST request
//       fetch("/find_route", {
//           method: "POST",
//           headers: {
//             "Content-Type": "application/json",
//           },
//           body: JSON.stringify({
//             from: parseInt(fromValue, 10), // Ép kiểu thành số nguyên
//             to: parseInt(toValue, 10),
//             departDate: departDateInput,
//           }),
//         })
//         .then((response) => response.json())
//         .then((data) => {
//           console.log(data);
//           const currentPath = window.location.pathname;
//           console.log(currentPath);
          

//           const container = document.querySelector(".result-flights");
//           console.log(container);

          
//           if (data.success) {
//             alert(`Tìm thấy tuyến đường: ${data}`);
//             container.innerHTML = "";
//             data.flights.forEach((item) => {
//               function formatTime(isoTime) {
//                 const timeObj = new Date(isoTime);
//                 const hours = timeObj.getHours().toString().padStart(2, '0');
//                 const minutes = timeObj.getMinutes().toString().padStart(2, '0');
//                 return `${hours}:${minutes}`;
//             }
//               container.innerHTML += `
//                     <div class="card rounded-pill px-5 py-10 m-5 shadow-sm">
//                         <div class="row g-0">
//                             <div class="col-md-4 text-center p-3">
//                                 <div class="w-100 h-100 d-flex align-items-center justify-content-around">
//                                     <div class="d-flex flex-column align-items-center">
//                                       <h5>${formatTime(item.depart_time)}</h5>
//                                       <p class="mb-0">${data.route.depart_airport}</p>
//                                       <small>Nhà ga 1</small>
//                                     </div>
//                                     <div class="d-flex flex-column align-items-center">
//                                         <span>Bay thẳng</span>
//                                         <div class="dotted-underline"></div>
//                                     </div>
//                                     <div class="d-flex flex-column align-items-center">
//                                         <h5>${formatTime(item.arrive_time)}</h5>
//                                         <p class="mb-0">${data.route.arrive_airport}</p>
//                                         <small>Nha ga 1</small>
//                                     </div>
//                                 </div>
//                             </div>
//                             <div class="col-md-5 border-start border-end p-3">
//                               <div class="w-100 h-100 d-flex flex-column align-items-center justify-content-center">
//                                 <div class="d-flex align-items-center">
//                                     <i class="bi bi-clock me-2"></i>
//                                     <span>Thời gian bay 2h 5 phút</span>
//                                 </div>
//                                 <div class="d-flex align-items-center mt-2">
//                                     <i class="bi bi-airplane me-2"></i>
//                                     <span>VN 224 Khai thác bởi Vietnam Airlines</span>
//                                 </div>
//                                 <a href="#" class="text-decoration-none mt-2 d-block">Chi tiết hành trình</a>
//                               </div>
//                             </div>
//                             <div class="col-md-3 p-3 text-center">
//                               <div class="mb-3">
//                                 <button class="btn btn-secondary w-100" disabled>PHỔ THÔNG <br> HẾT VÉ</button>
//                               </div>
//                               <div class="bg-warning rounded">
//                                   <span class="fw-bold">THƯƠNG GIA</span>
//                                 <div class="mt-2">
//                                     <span class="fs-4">từ 5.860.000</span> <small>VND</small>
//                                 </div>
//                               </div>
//                             </div>
//                         </div>
//                     </div>`;
//             });
//             // Kiểm tra và chuyển hướng sang trang /booking


//           } else {
//             alert(`Không tìm thấy tuyến đường. Lý do: ${data.message}`);
//           }
//         })
//         .catch((error) => {
//           console.error("Lỗi khi gửi yêu cầu:", error);
//         });
//     } else {
//       alert('Vui lòng chọn cả "From" và "To".');
//     }
//   });