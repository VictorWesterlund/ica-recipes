import time
import json
import requests

output_file = "recipes.json"
auth_file = ("_auth.json",'{\n\t"username":"",\n\t"password":""\n}')

sleep = 2

def load_JSON(f):
	with open(f) as f:
		data = json.load(f)

	return data

def dump_JSON(f,data):
	with open(f,"w", encoding="utf-8") as f:
		json.dump(data,f,ensure_ascii=False,indent=4)

class BasicAuthentication:

	endpoint = "https://handla.api.ica.se/api/login/"

	def __init__(self,username,password):
		self.ticket = None
		self.logoutKey = None

		self.login((username,password))

	def login(self,credentials):
		auth = requests.get(BasicAuthentication.endpoint, auth=(credentials))
		auth.status_code
		auth.raise_for_status()

		self.ticket = auth.headers["AuthenticationTicket"]
		self.logoutKey = auth.headers["LogoutKey"]

class ICA_recipes(BasicAuthentication):

	endpoint = "https://handla.api.ica.se/api/recipes/recipe/"

	def __init__(self,auth):
		super().__init__(auth["username"],auth["password"])
		self.headers = {
			"AuthenticationTicket": self.ticket
		}

	# Yield the next recipe
	def next_recipe(self):
		i = 1000
		limit = i + 5

		while True:
			endpoint = ICA_recipes.endpoint + str(i) + "/"
			recipe = requests.get(endpoint,headers=self.headers)

			data = (i,recipe.text)

			if(recipe.status_code != 200 or (limit and i >= limit)):
				data = (False,None)

			yield data
			i += 1

	# Save all recipes as JSON
	def save_all(self):
		recipes = []

		for recipe in self.next_recipe():
			index = recipe[0]
			if index == False:
				break

			data = recipe[1]

			recipes.append(data)
			print("Saved recipe from: " + ICA_recipes.endpoint + str(index) + "/")
			time.sleep(sleep)

		print("Didn't recieve OK from endpoint or reached limit. Assuming that was the last recipe.")
		print(f"Saving {len(recipes)} recipe(s) as '{output_file}'")
		dump_JSON(output_file,recipes)

# ----

try:
	f = load_JSON(auth_file[0])
	recipes = ICA_recipes(f)
	recipes.save_all()
	
except requests.exceptions.HTTPError as error:
	raise SystemExit(error)

except IOError as error:
	f = open(auth_file[0],"w")
	f.write(auth_file[1])
	f.close()
	print(auth_file[0] + " created")