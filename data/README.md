# Data

**Marketing A/B Testing** (Kaggle dataset by Favio Vázquez)
<https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing>

| column | meaning |
|---|---|
| `user id` | unique user |
| `test group` | `ad` (saw the advertisement, variant) or `psa` (saw a public-service announcement, control) |
| `converted` | `True` if the user bought the product |
| `total ads` | number of ads the user saw |
| `most ads day` | weekday on which the user saw the most ads |
| `most ads hour` | hour of day at which the user saw the most ads |

The raw CSV is not committed (size and licence). To download it:

```bash
pip install kaggle          # needs ~/.kaggle/kaggle.json (Kaggle → Settings → Create New Token)
kaggle datasets download -d faviovaz/marketing-ab-testing -p data --unzip
```

The notebook expects `data/marketing_AB.csv`.
