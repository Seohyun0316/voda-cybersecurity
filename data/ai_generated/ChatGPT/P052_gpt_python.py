keyword = input("°Ë»ö¾î: ")

sql = "SELECT * FROM products WHERE name LIKE %s"
cursor.execute(sql, ("%" + keyword + "%",))

results = cursor.fetchall()

for product in results:
    print(product)