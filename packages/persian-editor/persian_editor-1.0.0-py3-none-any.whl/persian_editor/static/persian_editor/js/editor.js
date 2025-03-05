// مقداردهی اولیه ویرایشگر
function initPersianEditor(elementId) {
    var editorDiv = document.getElementById(elementId + '_editor');
    var textarea = document.getElementById(elementId);
    if (!editorDiv || !textarea) return;
    // مخفی کردن تکست‌اریا
    textarea.style.display = "none";

    // Autosave: بازیابی محتوا از localStorage
    var autosaveKey = "persian_editor_" + elementId;
    if(localStorage.getItem(autosaveKey)) {
         editorDiv.innerHTML = localStorage.getItem(autosaveKey);
         textarea.value = editorDiv.innerHTML;
    }

    // به‌روزرسانی محتوا و ذخیره خودکار
    editorDiv.addEventListener("blur", function() {
        textarea.value = editorDiv.innerHTML;
        localStorage.setItem(autosaveKey, editorDiv.innerHTML);
    });
    editorDiv.addEventListener("input", function() {
        textarea.value = editorDiv.innerHTML;
        localStorage.setItem(autosaveKey, editorDiv.innerHTML);
    });

    // تنظیم رویداد برای آپلود تصویر
    var imageInput = document.getElementById(elementId + '_image_input');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            handleImageUpload(elementId, this.files[0]);
        });
    }
}

// اجرای دستورات قالب‌بندی پایه
function execCommand(editorId, command) {
    var editorDiv = document.getElementById(editorId + '_editor');
    if (!editorDiv) return;
    document.execCommand(command, false, null);
    editorDiv.focus();
}

// اجرای دستور با مقدار (برای تغییر رنگ)
function execCommandValue(editorId, command, value) {
    var editorDiv = document.getElementById(editorId + '_editor');
    if (!editorDiv) return;
    document.execCommand(command, false, value);
    editorDiv.focus();
}

// تغییر بین حالت WYSIWYG و HTML (source view)
function toggleSourceView(editorId) {
    var editorDiv = document.getElementById(editorId + '_editor');
    if (!editorDiv) return;
    if (editorDiv.getAttribute('data-source-view') === 'true') {
        // تبدیل به HTML تفسیرشده
        editorDiv.innerHTML = editorDiv.textContent;
        editorDiv.setAttribute('data-source-view', 'false');
    } else {
        // نمایش منبع HTML به صورت متن خام
        editorDiv.textContent = editorDiv.innerHTML;
        editorDiv.setAttribute('data-source-view', 'true');
    }
    editorDiv.focus();
}

// پاکسازی قالب‌بندی
function clearFormatting(editorId) {
    var editorDiv = document.getElementById(editorId + '_editor');
    if (!editorDiv) return;
    document.execCommand("removeFormat", false, null);
    editorDiv.focus();
}

// درخواست وارد کردن لینک از کاربر
function triggerLinkPrompt(editorId) {
    var url = prompt("آدرس لینک را وارد کنید:");
    if(url) {
        document.execCommand("createLink", false, url);
    }
}

// فعال‌سازی آپلود تصویر
function triggerImageUpload(editorId) {
    var imageInput = document.getElementById(editorId + '_image_input');
    if (imageInput) {
        imageInput.click();
    }
}

// مدیریت آپلود تصویر با AJAX
function handleImageUpload(editorId, file) {
    var editorDiv = document.getElementById(editorId + '_editor');
    if (!file || !editorDiv) return;

    var formData = new FormData();
    formData.append('image', file);

    var xhr = new XMLHttpRequest();
    // تنظیم مسیر endpoint آپلود تصویر؛ مطمئن شوید مسیر صحیح است
    xhr.open('POST', '/upload-image/', true);
    
    // افزودن CSRF token برای امنیت (با استفاده از کوکی‌ها)
    var csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
    }

    xhr.onload = function() {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.image_url) {
                insertImageAtCursor(editorDiv, response.image_url);
            } else {
                alert('خطا در آپلود تصویر.');
            }
        } else {
            alert('خطا در آپلود تصویر.');
        }
    };

    xhr.send(formData);
}

// دریافت CSRF token از کوکی‌ها
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// درج تصویر در مکان فعلی کرسر
function insertImageAtCursor(editorDiv, imageUrl) {
    var img = document.createElement('img');
    img.src = imageUrl;
    img.alt = 'تصویر آپلود شده';
    
    var selection = window.getSelection();
    if (selection.rangeCount > 0) {
        var range = selection.getRangeAt(0);
        range.insertNode(img);
        range.setStartAfter(img);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
    } else {
        editorDiv.appendChild(img);
    }
    
    // به‌روزرسانی تکست‌اریا
    var textarea = document.getElementById(editorDiv.id.replace('_editor', ''));
    if (textarea) {
        textarea.value = editorDiv.innerHTML;
    }
}

// تغییر حالت تمام صفحه
function toggleFullscreen(editorId) {
    var container = document.getElementById(editorId + '_container');
    if (!container) return;
    container.classList.toggle("fullscreen");
}
