
DELIMITER //
CREATE PROCEDURE mealswithcalcount(calcount int,cat varchar(20))
BEGIN
SELECT categories.recID, category, title, calories, prepTime, dateAdded FROM categories
JOIN Recipes
ON categories.recID = Recipes.recID
WHERE Recipes.calories >= calcount - 50 and Recipes.calories <= calcount +50 and Recipes.calories >= calcount and categories.category = cat;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE usermeals(AccId varchar(30))
BEGIN
SELECT p.planMID, Bfast, lunch, dinner from plan_assignments as p join meal_plan on p.planMID = meal_plan.planMID
WHERE p.AccID = AccID;
END //
DELIMITER ;

DELIMITER //
CREATE PROCEDURE setserving(mealID varchar(30), servings int)
BEGIN
UPDATE Meals
SET Meals.servings = servings
WHERE Meals.mealID = mealID;
END //
DELIMITER ;
