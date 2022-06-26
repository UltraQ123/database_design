function check_username(username) {
    if (username.length < 8 || username.length > 20) {
        window.alert("用户名长度不符合要求");
        return false
    }
    let username_pattern = /^[0-9a-zA-Z]+$/;
    if (!username_pattern.test(username)) {
        window.alert("用户名格式不符合要求");
        return false
    }
    return true;
}
function check_password(password) {
    if (password.length < 6 || password.length > 20) {
        window.alert("密码长度不符合要求");
        return false;
    }
    let sub = [/[0-9]/, /[a-zA-Z]/];
    let password_pattern = /^[0-9a-zA-Z_]+$/
    if (!password_pattern.test(password)) {
        window.alert("密码格式不符合要求");
        return false;
    }
    for (i in sub) {
        if (!sub[i].test(password)) {
            window.alert("密码格式不符合要求");
            return false;
        }
    }
}