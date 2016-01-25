from PiBrew import Recipe, Step

s1 = Step(name='step1_-1_50', span=-1, temperature=50)
s2 = Step(name='step2_-1_70', span=-1, temperature=70)
s3 = Step(name='step2_1_70', span=1, temperature=70)
s4 = Step(name='step3_1_80', span=1, temperature=80)


# r1 = Recipe(name='test1', slug='test1', steps=[s1, s2])
# r2 = Recipe(name='test2', slug='test2', steps=[s1, s3])
r3 = Recipe(name='test3', slug='test3', steps=[s1, s3, s4])

# r1.save()
# r2.save()
r3.save()
