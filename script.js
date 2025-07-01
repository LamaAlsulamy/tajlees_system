document.addEventListener('DOMContentLoaded', () => {
  const rooms = [
    { name: 'قاعة مكة', chairs: 31, rows: 1 },
    { name: 'قاعة الرياض', chairs: 62, rows: 2 },
    { name: 'قاعة المدينة', chairs: 93, rows: 3 },
    { name: 'قاعة الطائف', chairs: 31, rows: 1 },
    { name: 'قاعة الأمير نايف', chairs: 62, rows: 2 },
    { name: 'قاعة الملك سلمان', chairs: 93, rows: 3 },
    { name: 'قاعة الملك عبدالعزيز', chairs: 31, rows: 1 },
    { name: 'قاعة جدة', chairs: 62, rows: 2 },
    { name: 'قاعة الملك فهد', chairs: 93, rows: 3 }
  ];

  showRoomSelection(rooms);
});

function showRoomSelection(rooms) {
  const container = document.querySelector('.container');
  let html = `<h2>اختر القاعة:</h2>
    <select id="roomDropdown">
      <option value="" disabled selected>-- اختر القاعة --</option>`;

  rooms.forEach(room => {
    html += `<option value="${room.name},${room.chairs},${room.rows}">
      ${room.name} (${room.chairs} كرسي)
    </option>`;
  });

  html += `</select>
    <button id="confirmRoom">تأكيد</button>`;

  container.innerHTML = html;

  document.getElementById('confirmRoom').addEventListener('click', () => {
    const selected = document.getElementById('roomDropdown').value;
    if (!selected) return alert("الرجاء اختيار قاعة");

    const [roomName, chairCount, rowCount] = selected.split(',');
    loadGuestList(parseInt(chairCount));
  });
}

function loadGuestList(chairCount) {
  Papa.parse('data/guest-list.csv', {
    download: true,
    header: true,
    skipEmptyLines: true,
    complete: function(results) {
      const guests = results.data.map(g => ({
        name: g['الاسم'],
        category: parseInt(g['رقم الفئة'])
      }));
      showGuestSelection(guests, chairCount);
    },
    error: function(err) {
      alert("حدث خطأ أثناء تحميل أسماء الضيوف.");
      console.error(err);
    }
  });
}

function showGuestSelection(guests, chairCount) {
  const container = document.querySelector('.container');
  let selectedCount = 0;

  let html = `
    <h2>اختر الضيوف (الحد الأقصى: ${chairCount})</h2>
    <p id="seatCounter">المقاعد المتبقية: ${chairCount}</p>
    <div class="guest-list">`;

  guests.forEach((guest, index) => {
    html += `
      <label>
        <input type="checkbox" class="guest-check" data-index="${index}">
        ${guest.name} (فئة ${guest.category})
      </label><br>`;
  });

  html += `</div><br>
    <button id="confirmGuests">تأكيد الضيوف</button>`;

  container.innerHTML = html;

  const checkboxes = document.querySelectorAll('.guest-check');
  checkboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked) {
        if (selectedCount >= chairCount) {
          cb.checked = false;
          alert('لقد وصلت إلى الحد الأقصى للمقاعد!');
        } else {
          selectedCount++;
        }
      } else {
        selectedCount--;
      }
      document.getElementById('seatCounter').textContent = `المقاعد المتبقية: ${chairCount - selectedCount}`;
    });
  });

  document.getElementById('confirmGuests').addEventListener('click', () => {
    const selectedGuests = [];
    checkboxes.forEach(cb => {
      if (cb.checked) {
        const i = parseInt(cb.getAttribute('data-index'));
        selectedGuests.push(guests[i]);
      }
    });

    console.log("الضيوف المحددون:", selectedGuests);

    container.innerHTML = `<h2>تم اختيار ${selectedGuests.length} ضيفًا!</h2>
      <p>جاهز للترتيب حسب الفئة!</p>`;
    
    // 📌 Next step goes here: load class priority and sort seating
  });
}
