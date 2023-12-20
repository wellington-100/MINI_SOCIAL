{% load static %}
{% load custom_filters %}
<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="shortcut icon" type="image/png" href="{% static 'favicon.png' %}"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">


    <meta charset="UTF-8">
    <title>MINI SOCIAL</title>
    <style>
        body {
            font-family: Arial;
            background-color: #fff;
            margin: 0;
            overflow-x: hidden;
            height: 100vh;
        }
        .page-wrapper {
            display: flex;
            justify-content: center; /* Добавляем это свойство для центрирования дочерних элементов по горизонтали */
            align-items: flex-start; /* Добавляем это свойство для позиционирования дочерних элементов в начале родительского элемента по вертикали */
            height: 100vh;
        }
        .fixed-top-wrapper {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            padding: 10px 0;
            background-color: rgba(255, 255, 255, 0.9);
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 30px;
        }
        .center-buttons a {
            width: 150px;
            box-sizing: border-box;
        }
        .center-buttons {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .center-buttons a:not(:last-child) {
            margin-right: 20px;
        }
        .center-buttons .logout-link {
            flex-grow: 1;
            text-align: center;
        }
/* Fixed left block */
        .fixed-left-wrapper {
            position: fixed;
            top: 70px; /* Это значение устанавливается на основе высоты вашего .fixed-top-wrapper */
            left: 0;
            bottom: 0;
            width: 20%; /* Задайте ширину, которая вам подходит */
            overflow-y: auto; /* Это позволит содержимому блока прокручиваться, если оно не умещается */
        }
        .rounded-avatar {
            width: 50px;
            height: 50px;
            margin-left: 20px;
            border-radius: 50%;
            overflow: hidden;
            display: inline-block;
            flex-shrink: 0;
        }
        .rounded-avatar img {
            display: block;
            max-width: 100%;
            height: auto;
        }
        .menu-link {
            font-weight: bold;
            text-decoration: none;
            color: #000;
            margin-bottom: 10px;
            display: block;
            padding: 5px 0;
            margin: 10px;
            margin-left: 30px;
        }
        .menu-link:hover {
            background-color: #f5f5f5;
        }
/* Fixed left block */
        .logout-link {
            padding: 10px 20px;
            background-color: #C19A6B;
            color: black;
            border-radius: 10px;
            text-decoration: none;
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.1);
            border: 1px solid #ccc;
            margin-right: 50px;
        }
        .logout-link:hover {
            background-color: #E6BF83;
        }
        .profile-container {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 0;
        }
        .profile-container img {
            margin-right: 15px;
        }
        .content-wrapper {
            position: absolute; /* Абсолютное позиционирование */
            left: 50%; /* Центрирование блока относительно экрана */
            transform: translateX(-50%); /* Дополнительное смещение для точного центрирования */
            width: auto; 
            max-width: 750px; 
            padding: 40px;
            text-align: center;
            margin-top: 70px; 
        }
        .empty-right-wrapper {
            flex: 2;
        }
        .logo-image {
            display: block;
            margin: 0 auto;
            width: 70%;
        }
        .links-container {
            margin: 20px 0;
        }
        .links-container a {
            display: block;
            font-size: 16px;
            text-decoration: none;
            background-color: #C19A6B;
            color: #fff;
            padding: 10px 20px;
            border-radius: 10px;
            margin: 20px auto;
            width: 200px;
            cursor: pointer;
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.1);
            border: 1px solid #ccc;
            font-weight: bold;
        }
        .links-container a:hover {
            background-color: #E6BF83;
        }
        .menu-link {
            font-weight: bold;
            text-decoration: none;
            color: #000;
            margin-bottom: 10px;
            display: block;
            padding: 5px 0;
            margin: 10px;
            margin-left: 20px;
        }
        .menu-link:hover {
            background-color: #f5f5f5;
        }
        .form-group {

            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .form-group label {
            margin-right: 10px;
            width: 150px;  /* или любую другую ширину, которая вам подходит */
            display: inline-block;
            
        }
        .form-group input[type="text"],
        .form-group input[type="email"],
        .form-group input[type="password"],
        .form-group input[type="file"] {
            width: 200px;
        }
        .logo-image {
            display: block;
            margin: 0 auto;
            width: 70%;
        }
        h1 {
            color: black;
            font-size: 24px;
            margin: 20px 0;
            style="margin-top: 30px;"
        }
        .error-messages {
            color: red;
            margin: 20px 0;
            font-weight: bold;
        }
        form {
            display: inline-block;
            margin: 20px 0;
            border-radius: 10px;
        }
        form input  {
            display: block;
            font-size: 16px;
            width: 200px;
            padding: 10px;
            margin: 10px auto;
            border-radius: 5px;
            border: 1px solid #ccc;
            color: black;
            background-color: #fff;
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.1);
            
        }
        form button {
            display: block;
            font-size: 16px;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background-color: #C19A6B;
            color: black;
            margin: 20px auto;
            cursor: pointer;
            width: 230px;
            font-weight: bold;
            align-items: center;
        }
        form button:hover {
            background-color: #E6BF83;
        }
        .footer {
            position: relative;
            margin-top: 20px;
            text-align: center;
            color: #333;
        }
        p{
            margin-bottom: 0px;"
        }
        .bold-link {
            font-weight: bold;
            text-decoration: none;
            color: inherit;
        }
        .bold-link:hover {
            text-decoration: underline;
        }
        .footer {
            position: relative;
    
            text-align: center;
            color: #333;
        }
    </style>

</head>
<body>
    <div class="page-wrapper">
        <div class="fixed-top-wrapper">
            .....
        </div>

        <!-- Fixed left block -->
        <div class="fixed-left-wrapper">
            .....
        </div>
        <!-- Fixed left block -->

        <div class="content-wrapper">
            <h1>EDIT PROFILE</h1>
                ....
            </div>
            <br/>
            {% endif %}



            <form action="/user/profile/save/" method="POST" enctype="multipart/form-data" id="registerForm">
                 
             
                <button type="submit">SAVE</button>
                {% csrf_token %}
            </form>

            <p class="footer">{{ current_year }} &copy; MSM corp </p><br><br>
        </div>
        <div class="empty-right-wrapper"></div>
    </div>
</body>
</html>
