function toggleDarkMode() {
  const overlay = document.getElementById('fadeOverlay');
  const body = document.body;

  overlay.classList.add('active');

  setTimeout(() => {
    const isDark = body.classList.contains('dark');
    if (isDark) {
      body.classList.remove('dark');
      body.classList.add('light');
      localStorage.setItem('darkMode', 'false');
    } else {
      body.classList.remove('light');
      body.classList.add('dark');
      localStorage.setItem('darkMode', 'true');
    }

    setTimeout(() => {
      overlay.classList.remove('active');
    }, 400);
  }, 200);
}

window.onload = () => {
  const saved = localStorage.getItem('darkMode');
  const body = document.body;

  if (saved === 'true') {
    body.classList.remove('light');
    body.classList.add('dark');
  } else {
    body.classList.remove('dark');
    body.classList.add('light');
  }

  const savedUser = localStorage.getItem('rememberUser');
  if (savedUser) {
    document.getElementById('faculty_name').value = savedUser;
    document.getElementById('rememberMe').checked = true;
  }
};

function storeRememberMe() {
  const remember = document.getElementById('rememberMe').checked;
  const user = document.getElementById('faculty_name').value;
  if (remember) {
    localStorage.setItem('rememberUser', user);
  } else {
    localStorage.removeItem('rememberUser');
  }
}

//dashbord code.......!!!!


window.onload = () => {
  // ... theme toggle + rememberMe logic ...

  // Dummy attendance chart
  const ctx1 = document.getElementById('attendanceChart');
  if (ctx1) {
    new Chart(ctx1, {
      type: 'bar',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{
          label: 'Attendance %',
          data: [90, 85, 80, 88, 92],
          backgroundColor: '#4facfe'
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
  }

  const ctx2 = document.getElementById('subjectChart');
  if (ctx2) {
    new Chart(ctx2, {
      type: 'pie',
      data: {
        labels: ['Math', 'DBMS', 'OS'],
        datasets: [{ data: [30, 50, 20], backgroundColor: ['#4facfe', '#00f2fe', '#a2e'] }]
      }
    });
  }

  const ctx3 = document.getElementById('dailyChart');
  if (ctx3) {
    new Chart(ctx3, {
      type: 'line',
      data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{ label: 'Present', data: [25, 26, 24, 27, 30], borderColor: '#4facfe' }]
      }
    });
  }
  const front = document.querySelector(".stack-front");
  const back = document.querySelector(".stack-back");

  if (front && back) {
    setInterval(() => {
      front.classList.toggle("stack-front");
      front.classList.toggle("stack-back");
      back.classList.toggle("stack-front");
      back.classList.toggle("stack-back");
    }, 5000); // every 5 seconds
  }
  const cards = document.querySelectorAll(".lecture-card");
  let index = 0;

  if (cards.length > 1) {
    cards[0].classList.add("active");

    setInterval(() => {
      cards[index].classList.remove("active");
      index = (index + 1) % cards.length;
      cards[index].classList.add("active");
    }, 5000); // switch every 5 seconds
  }
};

