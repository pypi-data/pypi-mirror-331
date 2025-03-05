.. |package-name| replace:: mapping-kit

.. |pypi-version| image:: https://img.shields.io/pypi/v/mapping-kit?label=PyPI%20Version&color=4BC51D
   :alt: PyPI Version
   :target: https://pypi.org/projects/mapping-kit/

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/mapping-kit?label=PyPI%20Downloads&color=037585
   :alt: PyPI Downloads
   :target: https://pypi.org/projects/mapping-kit/

mapping-kit
###########

|pypi-version| |pypi-downloads|

Description
***********

Provides
 - AttributeDict (keys accessible as dot-denoted attributes, remains subscriptable)
 - GroupDict (groups keys based on prefix, makes it easy to write complex configuration in a single dictionary and access it easily)
 - SuperDict (a dictionary that is defaultdict, OrderedDict, case-insensitive, and recursive,, each customizable by user)

Examples of AttributeDict:

.. code-block:: python

   from mapping_kit import AttributeDict

   # All the standard ways that a Python dict can be created in, can be used to
   # create AttributeDict. It can also be used as a normal dictionary.

   my_dict = {
       "first_name": "Charlie",
       "last_name": "Brown",
   }
   from_dict = AttributeDict(**my_dict)
   print("Hello", from_dict.first_name, from_dict["last_name"])
   # Hello Charlie Brown

   my_tuples = [("model", "Hindustan Ambassador"),
                ("production", "1957-2014")]
   from_tuples = AttributeDict(my_tuples)
   print(from_tuples.model, "was produced in the years", from_tuples["production"])
   # Hindustan Ambassador was produced in the years 1957-2014


Examples of GroupDict:

.. code-block:: python

   from mapping_kit import GroupDict

   my_dict = {
       "#Version": "1.4.9a1",
       "beverages": {
           "_lassi": "A yoghurt based beverage",
           "_aamras": "Thick mango pulp",
           "*jaljeera": "Spices mixed in water, out of stock",
           "*alcoholic_drinks": {
               "beer": "4-6% alcohol",
               "red_wine": "5.5-10% alcohol"
           },
       },
       "appetizers": {
           "_pani_puri": "Masala water filled crispy puffed bread",
           "!chicken_pakora": "Deep-fried chicken stuffing in Indian pakoras",
           "_aloo_chaat": "Potato with spicy gravy",
           "!prawn_toast": "Sesame and prawns rolled in bread"
       }
   }

   gd = GroupDict(my_dict,
                  grouping={"#": "comment",  # arbitrary group names
                            "_": "vegetarian",
                            "!": "non_vegetarian",
                            "*": "not_available"},
                  recursive=True,
                  ignorecase_get=True)

   # Accessing group `comment`
   print("The version is", gd.comment["version"])
   # The version is 1.4.9a1

   for key, value in gd.comment.items():
       print("key:", key, ", value:", value)
   # key: Version , value: 1.4.9a1

   # Chained groups
   veg_appetizers = gd.public["appetizers"].vegetarian
   print("Vegetarian appetizers are:")
   for key in veg_appetizers.keys():
       print(f"  {key}")
   # Vegetarian appetizers are:
   #   pani_puri
   #   aloo_chaat

   beverages_not_available = gd["beverages"].not_available
   print("Beverages not available are:")
   for bna, bna_desc in beverages_not_available.items():
       if isinstance(bna_desc, dict):
           for bna_sub, bna_sub_desc in bna_desc.public.items():
               print(f"  {bna_sub} ({bna_sub_desc})")
       else:
           print(f"  {bna} ({bna_desc})")
   # Beverages not available are:
   #   jaljeera (Spices mixed in water, out of stock)
   #   beer (4-6% alcohol)
   #   red_wine (5.5-10% alcohol)


Examples of SuperDict:

.. code-block:: python

   from mapping_kit import SuperDict

   # TODO

Note: This is an alpha version, and things may change quite a bit.