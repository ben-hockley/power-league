import random

# Generate a random name made up of a first name and a last name.
# Picks at random from a list of 100 common first and last names for American Football players.
# 10000 possible names.
first_names = [
    "James", "John", "Michael", "Chris", "David", "Robert", "Josh", "Matt", "Mike", "Kevin",
    "Jason", "Brian", "Brandon", "Eric", "Justin", "Ryan", "Anthony", "Alex", "Tyler", "Jordan",
    "Andrew", "Kyle", "Derrick", "Aaron", "Mark", "Steve", "Nick", "Daniel", "Sam", "Tom",
    "Ben", "Cameron", "Travis", "Jared", "Zach", "Patrick", "Sean", "Greg", "Tim", "Joe",
    "Will", "Corey", "Marcus", "Jonathan", "Devin", "Logan", "Cody", "Darren", "Troy", "Paul",
    "Eddie", "Ray", "Larry", "Frank", "Jalen", "Austin", "Christian", "Trevor", "Adam", "Phillip",
    "Randy", "Ronald", "George", "Leonard", "Malik", "Jamal", "Darius", "Calvin", "Allen", "Chad",
    "Garrett", "Blake", "Eli", "Jake", "Desmond", "Quincy", "Fred", "Jerry", "Lamar", "Kenny",
    "Antonio", "Terrance", "Marvin", "Isaiah", "Javon", "Darrell", "Curtis", "Dennis", "Billy", "Grant",
    "Terry", "Harold", "Ricky", "Bruce", "Wesley", "Donte", "Marlon", "Omar", "Andre", "Nathan"
]
last_names = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Wilson", "Moore", "Taylor", "Anderson",
    "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Robinson", "Clark", "Lewis", "Walker",
    "Hall", "Allen", "Young", "King", "Wright", "Scott", "Hill", "Green", "Adams", "Baker",
    "Nelson", "Mitchell", "Carter", "Roberts", "Evans", "Turner", "Phillips", "Campbell", "Parker", "Edwards",
    "Collins", "Stewart", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey",
    "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward", "Brooks", "Gray", "James", "Watson",
    "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins", "Patterson",
    "Powell", "Long", "Simmons", "Foster", "Gonzalez", "Bryant", "Alexander", "Russell", "Griffin", "Diaz",
    "Hayes", "Myers", "Ford", "Hamilton", "Graham", "Sullivan", "Wallace", "Woods", "Cole", "West",
    "Jordan", "Owens", "Reyes", "Fisher", "Ellis", "Harrison", "Gibson", "Murray", "Freeman", "Hunter"
]

def get_random_fname():
    """
    Get a random first name from the list.
    """
    return random.choice(first_names)

def get_random_lname():
    """
    Get a random last name from the list.
    """
    return random.choice(last_names)