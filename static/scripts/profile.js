document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('.plus').addEventListener('click', function () {
        console.log('this works')
        document.querySelector('.modal-title').innerHTML = "Add Member"
        document.querySelector('.modal-bg').style.display = 'flex';
        let link = "/team/";
        let suffix = "/add_member"
        let l = link.concat(team, suffix)
        document.querySelector('.modal-form').action = l;
        document.getElementById('buttonprofile').innerText = "Add";
        document.querySelector('#member-params').name = "email";
        console.log("link added");

    });

    document.querySelector('.close').addEventListener('click', function () {
        document.querySelector('.modal-bg').style.display = 'none'

    });

    document.querySelector('.deleteteam').addEventListener('click', function () {
        console.log('this works')
        document.querySelector('.modal-title').innerHTML = "Delete Team"
        document.querySelector('.modal-bg').style.display = 'flex';
        let link = "/team/";
        let suffix = "/delete_team"
        let l = link.concat(team, suffix)
        console.log(l)
        document.querySelector('.modal-form').action = l;
        document.querySelector('#member-params').name = "team";
        document.getElementById('buttonprofile').innerText = "Delete"
        document.querySelector('#member-params').placeholder = "Please enter your team to confirm";
    });

    document.querySelector('.removemember').addEventListener('click', function () {
        console.log('this works')
        document.querySelector('.modal-title').innerHTML = "Remove Member"
        document.querySelector('.modal-bg').style.display = 'flex';
        let link = "/team/";
        let suffix = "/remove_member"
        let l = link.concat(team, suffix)
        document.querySelector('.modal-form').action = l;
        document.getElementById('buttonprofile').innerText = "Remove"
        document.querySelector('#member-params').name = "email";
    });
});