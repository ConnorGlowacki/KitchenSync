from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, Table, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, relationship, Mapped, declarative_base
from typing import List

db_file = 'test.db'

engine = create_engine(f'sqlite:///{db_file}', echo=True)

Session = sessionmaker(bind=engine)

Base = declarative_base()

# Define the association table for the many-to-many relationship
recipe_ingredient_association = Table(
    'recipe_ingredient_association',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipes.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)

# Define the RecipeIngredient table for the many-to-many-to-one relationship
class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredient'

    recipe_id = Column(Integer, ForeignKey('recipes.id'), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), primary_key=True)
    amount = Column(Float)

    # Define the many-to-one relationship with Recipe and Ingredient
    recipe = relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = relationship('Ingredient', back_populates='recipe_ingredients')

# Define the Ingredient dataclass
@dataclass
class Ingredient(Base):
    __tablename__ = 'ingredients'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    amount: str = Column(String)

    # Define the many-to-many relationship with Recipe
    recipes: Mapped[List['Recipe']] = relationship(
        'Recipe',
        secondary=recipe_ingredient_association,
        back_populates='ingredients'
    )

    # Define the one-to-many relationship with RecipeIngredient
    recipe_ingredients: Mapped[List[RecipeIngredient]] = relationship('RecipeIngredient', back_populates='ingredient')

# Define the Recipe dataclass
@dataclass
class Recipe(Base):
    __tablename__ = 'recipes'

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String)
    instructions: str = Column(String)

    # Define the many-to-many relationship with Ingredient
    ingredients: Mapped[List[Ingredient]] = relationship(
        'Ingredient',
        secondary=recipe_ingredient_association,
        back_populates='recipes'
    )

    # Define the one-to-many relationship with RecipeIngredient
    recipe_ingredients: Mapped[List[RecipeIngredient]] = relationship('RecipeIngredient', back_populates='recipe')

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a session object to interact with the database
session = Session()

# Create some example data
flour = Ingredient(name='Flour', amount='1 cup')
water = Ingredient(name='Water', amount='1/2 cup')
salt = Ingredient(name='Salt', amount='1 tsp')
dough = Recipe(name='Dough', instructions='Mix flour, water, and salt')
dough.ingredients.extend([flour, water, salt])

dough_flour = RecipeIngredient(recipe=dough, ingredient=flour, amount=1.5)
dough_water = RecipeIngredient(recipe=dough, ingredient=water, amount=0.75)
dough_salt = RecipeIngredient(recipe=dough, ingredient=salt, amount=0.5)

#
session.add_all([flour, water, salt, dough, dough_flour, dough_salt, dough_water])

# Query the data
recipes = session.query(Recipe).all()
for recipe in recipes:
    print(recipe.name)
    print('Ingredients:')
    for ingredient in recipe.ingredients:
        print(f'{ingredient.amount} {ingredient.name}')
    print()
    
# Close the session
session.close()