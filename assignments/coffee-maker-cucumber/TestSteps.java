package edu.ncsu.csc326.coffeemaker;

import static org.junit.Assert.*;
import cucumber.api.java.en.Given;
import cucumber.api.java.en.When;
import cucumber.api.java.en.Then;
import edu.ncsu.csc326.coffeemaker.UICmd.*;

/** User-story integration steps. All application actions use UI commands. */
public class TestSteps {
    private CoffeeMakerUI ui;

    private void send(Command command) {
        ui.UI_Input(command);
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

    @Given("^a fresh coffee maker$")
    public void fresh() {
        ui = new CoffeeMakerUI(new CoffeeMaker(new RecipeBook(), new Inventory()));
        assertEquals(CoffeeMakerUI.Mode.WAITING, ui.getMode());
        assertEquals(0, ui.getMoneyInserted());
        assertEquals(0, ui.getMoneyInTray());
    }

    @Given("^the standard three recipes are available$")
    public void standardRecipes() throws Exception {
        add("Coffee", 50, 3, 1, 1, 0);
        add("Latte", 70, 2, 3, 1, 0);
        add("Mocha", 90, 2, 2, 1, 3);
        count(3);
    }

    @When("^I select service (-?\\d+)$")
    public void service(int button) { send(new ChooseService(button)); }

    @When("^I reset the current operation$")
    public void reset() { send(new Reset()); }

    @When("^I add recipe \"([^\"]+)\" priced (\\d+) using (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void add(String name, int price, int coffee, int milk,
                    int sugar, int chocolate) throws Exception {
        service(1);
        mode("ADD_RECIPE");
        send(new DescribeRecipe(recipe(name, price, coffee, milk, sugar, chocolate)));
    }

    @When("^I delete recipe at index (-?\\d+)$")
    public void delete(int index) {
        service(2);
        mode("DELETE_RECIPE");
        send(new ChooseRecipe(index));
    }

    @When("^I select recipe at index (-?\\d+) for editing$")
    public void selectEdit(int index) {
        service(3);
        mode("EDIT_RECIPE");
        send(new ChooseRecipe(index));
    }

    @When("^I submit edited recipe named \"([^\"]+)\" priced (\\d+) using (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void edit(String name, int price, int coffee, int milk,
                     int sugar, int chocolate) throws Exception {
        mode("EDIT_RECIPE");
        send(new DescribeRecipe(recipe(name, price, coffee, milk, sugar, chocolate)));
    }

    @When("^I add inventory ([-\\d]+) coffee ([-\\d]+) milk ([-\\d]+) sugar ([-\\d]+) chocolate$")
    public void addStock(int coffee, int milk, int sugar, int chocolate) {
        service(4);
        mode("ADD_INVENTORY");
        send(new AddInventory(coffee, milk, sugar, chocolate));
    }

    @When("^I insert (-?\\d+) money units$")
    public void insert(int amount) { send(new InsertMoney(amount)); }

    @When("^I purchase recipe at index (-?\\d+)$")
    public void purchase(int index) {
        service(6);
        mode("PURCHASE_BEVERAGE");
        send(new ChooseRecipe(index));
    }

    @When("^I collect the returned money$")
    public void collect() { send(new TakeMoneyFromTray()); }

    @Then("^the machine mode is (\\w+)$")
    public void mode(String expected) {
        assertEquals(CoffeeMakerUI.Mode.valueOf(expected), ui.getMode());
    }

    @Then("^the operation status is (\\w+)$")
    public void status(String expected) {
        assertEquals(CoffeeMakerUI.Status.valueOf(expected), ui.getStatus());
    }

    @Then("^the recipe book contains (\\d+) recipes$")
    public void count(int expected) {
        int actual = 0;
        for (Recipe r : ui.getRecipes()) if (r != null) actual++;
        assertEquals(expected, actual);
    }

    @Then("^recipe at index (\\d+) is empty$")
    public void empty(int index) { assertNull(ui.getRecipes()[index]); }

    @Then("^recipe at index (\\d+) is \"([^\"]+)\" priced (\\d+) using (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void recipeEquals(int index, String name, int price, int coffee,
                             int milk, int sugar, int chocolate) {
        Recipe r = ui.getRecipes()[index];
        assertNotNull(r);
        assertEquals(name, r.getName());
        assertEquals(price, r.getPrice());
        assertEquals(coffee, r.getAmtCoffee());
        assertEquals(milk, r.getAmtMilk());
        assertEquals(sugar, r.getAmtSugar());
        assertEquals(chocolate, r.getAmtChocolate());
    }

    @Then("^the inserted money is (\\d+)$")
    public void inserted(int expected) { assertEquals(expected, ui.getMoneyInserted()); }

    @Then("^the return tray contains (\\d+) money units$")
    public void tray(int expected) { assertEquals(expected, ui.getMoneyInTray()); }

    @Then("^the inventory report shows (\\d+) coffee (\\d+) milk (\\d+) sugar (\\d+) chocolate$")
    public void stock(int coffee, int milk, int sugar, int chocolate) {
        // This is a user-visible check, not direct access to Inventory fields.
        mode("WAITING");
        service(5);
        mode("CHECK_INVENTORY");
        CheckInventory command = new CheckInventory();
        send(command);
        assertEquals("Coffee: " + coffee + "\nMilk: " + milk + "\nSugar: "
                + sugar + "\nChocolate: " + chocolate + "\n", command.getInventory());
        mode("WAITING");
        status("OK");
    }
}
