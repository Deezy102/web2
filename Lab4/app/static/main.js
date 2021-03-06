'use strict';

var myModalEl = document.getElementById('delete-user-modal')
myModalEl.addEventListener('show.bs.modal', function (event) {
    let form = this.querySelector('form');
    form.action = event.relatedTarget.dataset.url;

    let userNameElement = document.getElementById('user-name');
    userNameElement.innerHTML = event.relatedTarget.closest('tr').querySelector('.full-user-name').textContent;
})