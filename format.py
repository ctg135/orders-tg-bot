import db



def format_menu_list(menu: db.Food) -> str:
    '''
    Возвращает отформатированный список меню
    '''
    result = ''
    last_category = 0
    for food in menu:
        if food.category != last_category:
            last_category = food.category
            match last_category:
                case 1:
                    result += '\n<i>Первые блюда</i>\n'
                case 2:
                    result += '\n<i>Вторые блюда</i>\n'
                case 3:
                    result += '\n<i>Салаты</i>\n'
                case 4:
                    result += '\n<i>Напитки</i>\n'
        result += f' {food.name} {food.price} руб.\n'
    return result

