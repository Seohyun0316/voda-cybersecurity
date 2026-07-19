from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# SQLite 메모리 데이터베이스 사용 (실제 서비스에서는 MySQL, PostgreSQL 등으로 변경 가능)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- 서버 시작 시 테스트용 임시 데이터 세팅 ---
@app.before_request
def create_tables():
    # 테이블 생성 규칙이 한 번만 실행되도록 설정
    db.create_all()
    
    # 중복 삽입 방지 (메모리 DB가 비어있을 때만 샘플 입력)
    if not db.session.execute(text("SELECT 1 FROM recipes")).fetchone():
        # 1. 레시피 삽입
        db.session.execute(text("INSERT INTO recipes (title, instructions) VALUES ('김치볶음밥', '1. 김치와 밥을 볶는다. 2. 끝')"))
        db.session.execute(text("INSERT INTO recipes (title, instructions) VALUES ('삼겹살 김치찌개', '1. 삼겹살을 굽다 김치를 넣고 끓인다.')"))
        db.session.execute(text("INSERT INTO recipes (title, instructions) VALUES ('삼겹살 구이', '1. 삼겹살을 불판에 굽는다.')"))
        
        # 2. 재료 삽입
        db.session.execute(text("INSERT INTO ingredients (name) VALUES ('김치')"))
        db.session.execute(text("INSERT INTO ingredients (name) VALUES ('삼겹살')"))
        db.session.execute(text("INSERT INTO ingredients (name) VALUES ('밥')"))
        
        # 3. 매핑 데이터 삽입
        # 김치볶음밥 (김치=1, 밥=3)
        db.session.execute(text("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (1, 1, '1컵')"))
        db.session.execute(text("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (1, 3, '1공기')"))
        # 삼겹살 김치찌개 (김치=1, 삼겹살=2)
        db.session.execute(text("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (2, 1, '200g')"))
        db.session.execute(text("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (2, 2, '150g')"))
        # 삼겹살 구이 (삼겹살=2)
        db.session.execute(text("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (3, 2, '300g')"))
        
        db.session.commit()


# --- DB 스키마 정의 ---
class Recipe(db.Model):
    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    ingredient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.ingredient_id'), primary_key=True)
    amount = db.Column(db.String(50))


# --- API 엔드포인트 구현 ---

@app.route('/api/search', methods=['GET'])
def search_recipes():
    # 쿼리 스트링에서 ingredients 가져오기 (예: /api/search?ingredients=김치,삼겹살)
    ingredients_raw = request.args.get('ingredients', '')
    
    if not ingredients_raw:
        return jsonify({"error": "검색할 재료를 입력해주세요."}), 400
    
    # 쉼표 구분자로 들어온 재료들을 리스트로 변환
    search_list = [i.strip() for i in ingredients_raw.split(',') if i.strip()]
    ingredient_count = len(search_list)
    
    if ingredient_count == 0:
        return jsonify({"error": "유효한 재료가 없습니다."}), 400

    # SQL 인젝션을 방지하기 위해 플레이스홀더(:val0, :val1...)를 동적으로 생성
    placeholders = ", ".join([f":val{i}" for i in range(ingredient_count)])
    
    # 입력한 재료를 "모두(AND)" 포함하는 레시피 찾기 쿼리 작성
    query_str = f"""
        SELECT r.recipe_id, r.title, r.instructions
        FROM recipes r
        JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        WHERE i.name IN ({placeholders})
        GROUP BY r.recipe_id, r.title, r.instructions
        HAVING COUNT(DISTINCT i.name) = :exact_count
    """
    
    # 파라미터 바인딩 딕셔너리 생성
    bind_params = {f"val{i}": name for i, name in enumerate(search_list)}
    bind_params["exact_count"] = ingredient_count

    # 쿼리 실행
    result = db.session.execute(text(query_str), bind_params).fetchall()
    
    # 결과 포맷팅
    recipes = []
    for row in result:
        recipes.append({
            "recipe_id": row.recipe_id,
            "title": row.title,
            "instructions": row.instructions
        })
        
    return jsonify({
        "search_ingredients": search_list,
        "count": len(recipes),
        "recipes": recipes
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)