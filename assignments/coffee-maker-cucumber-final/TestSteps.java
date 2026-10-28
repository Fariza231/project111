package edu.ncsu.csc326.coffeemaker;

import static org.junit.Assert.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import cucumber.api.java.en.Given;
import cucumber.api.java.en.When;
import cucumber.api.java.en.Then;
import edu.ncsu.csc326.coffeemaker.UICmd.*;

/** Integration tests using only public UI commands and observations. */
public class TestSteps {
    private CoffeeMakerUI ui;

    @Given("^a new coffee maker with an empty recipe book$")
    public void start() {
        ui = new CoffeeMakerUI(new CoffeeMaker(new RecipeBook(), new Inventory()));
    }

    private Recipe recipe(String name, int price, int coffee, int milk,
                          int sugar, int chocolate) throws Exception {
        Recipe r = new Recipe();
        r.setName(name);
        r.setPrice(Integer.toString(price));
        r.setAmtCoffee(Integer.toString(coffee));
        r.setAmtMilk(Integer.toString(milk));
        r.setAmtSugar(Integer.toString(sugar));
        r.setAmtChocolate(Integer.toString(chocolate));
        return r;
    }

    private int index(String name) {
        Recipe[] recipes = ui.getRecipes();
        for (int i = 0; i < recipes.length; i++) {
            if (recipes[i] != null && name.equals(recipes[i].getName())) return i;
        }
        fail("Recipe not found: " + name);
        return -1;
    }

    @When("^I choose menu service (\\d+)$")
    public void service(int number) { ui.UI_Input(new ChooseService(number)); }

    @Then("^the current mode is (\\w+)$")
    public void mode(String name) {
        assertEquals(CoffeeMakerUI.Mode.valueOf(name), ui.getMode());
    }

    @Then("^the last status is (\\w+)$")
    public void status(String name) {
        assertEquals(CoffeeMakerUI.Status.valueOf(name), ui.getStatus());
    }

    @When("^I register \"([^\"]+)\" priced (\\d+) with (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void add(String name, int price, int coffee, int milk,
                    int sugar, int chocolate) throws Exception {
        service(1);
        ui.UI_Input(new DescribeRecipe(recipe(name, price, coffee, milk, sugar, chocolate)));
    }

    @Given("^three standard recipes have been registered$")
    public void standard() throws Exception {
        add("Coffee", 50, 3, 1, 1, 0);
        status("OK");
        add("Latte", 70, 2, 3, 1, 0);
        status("OK");
        add("Mocha", 90, 2, 2, 1, 3);
        status("OK");
    }

    @Then("^there are (\\d+) registered recipes$")
    public void count(int expected) {
        int count = 0;
        for (Recipe r : ui.getRecipes()) if (r != null) count++;
        assertEquals(expected, count);
    }

    @Then("^recipe \"([^\"]+)\" costs (\\d+) and requires (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void contents(String name, int price, int coffee, int milk,
                         int sugar, int chocolate) {
        Recipe r = ui.getRecipes()[index(name)];
        assertEquals(price, r.getPrice());
        assertEquals(coffee, r.getAmtCoffee());
        assertEquals(milk, r.getAmtMilk());
        assertEquals(sugar, r.getAmtSugar());
        assertEquals(chocolate, r.getAmtChocolate());
    }

    @When("^I remove recipe \"([^\"]+)\"$")
    public void remove(String name) {
        int selected = index(name);
        service(2);
        ui.UI_Input(new ChooseRecipe(selected));
    }

    @Then("^recipe \"([^\"]+)\" is no longer listed$")
    public void absent(String name) {
        for (Recipe r : ui.getRecipes()) {
            if (r != null) assertFalse(name.equals(r.getName()));
        }
    }

    @When("^I edit \"([^\"]+)\" submitting name \"([^\"]+)\" price (\\d+) and (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void edit(String originalName, String submittedName, int price,
                     int coffee, int milk, int sugar, int chocolate) throws Exception {
        int selected = index(originalName);
        service(3);
        ui.UI_Input(new ChooseRecipe(selected));
        ui.UI_Input(new DescribeRecipe(recipe(submittedName, price, coffee, milk, sugar, chocolate)));
    }

    @When("^I replenish (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void replenish(int coffee, int milk, int sugar, int chocolate) {
        service(4);
        ui.UI_Input(new AddInventory(coffee, milk, sugar, chocolate));
    }

    @Then("^the displayed stock is (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void stock(int coffee, int milk, int sugar, int chocolate) {
        service(5);
        CheckInventory command = new CheckInventory();
        ui.UI_Input(command);
        String report = command.getInventory();
        assertNotNull("Inventory report must be available", report);
        ingredient(report, "Coffee", coffee);
        ingredient(report, "Milk", milk);
        ingredient(report, "Sugar", sugar);
        ingredient(report, "Chocolate", chocolate);
        mode("WAITING");
    }

    private void ingredient(String report, String label, int expected) {
        // Check numeric content, allowing harmless differences in line endings
        // and whitespace rather than requiring a particular report layout.
        Matcher m = Pattern.compile("(?im)^\\s*" + label + "\\s*:\\s*(-?\\d+)\\s*$").matcher(report);
        assertTrue("Missing inventory entry: " + label, m.find());
        assertEquals(label, expected, Integer.parseInt(m.group(1)));
    }

    @When("^I pay (\\d+) and buy \"([^\"]+)\"$")
    public void purchase(int amount, String name) {
        int selected = index(name);
        service(6);
        ui.UI_Input(new InsertMoney(amount));
        ui.UI_Input(new ChooseRecipe(selected));
    }

    @Then("^the change tray contains (\\d+)$")
    public void change(int amount) { assertEquals(amount, ui.getMoneyInTray()); }

    @Then("^the inserted balance is (\\d+)$")
    public void balance(int amount) { assertEquals(amount, ui.getMoneyInserted()); }

    @When("^I empty the change tray$")
    public void emptyTray() { ui.UI_Input(new TakeMoneyFromTray()); }
}
