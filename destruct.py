import pandas as pd


class Destruct:

    def __init__(self, df, test_cols=None):
        self._df = df
        self._test_cols = test_cols

    @staticmethod
    def _create_df(file, col):
        combo_df = pd.concat(pd.read_excel(file, sheet_name=None))
        combo_df = combo_df.dropna(thresh=4, axis=0)
        filter_1 = combo_df.iloc[:, col] != 'STRENGTH'
        filter_2 = combo_df.iloc[:, col] != '(ppi)'
        combo_df = combo_df[filter_1 & filter_2]
        return combo_df

    @classmethod
    def fusion(cls, file_1, file_2):
        fusion_df = Destruct._create_df(file_1, file_2, 1)
        fusion_df.columns = ['Destruct', 'Shear Strength', 'Shear Break Code', 'B',
                             'Top Peel Strength', 'Top Peel Break Code', 'G',
                             'Bottom Peel Strength', 'Bottom Peel Break Code', 'H']
        fusion_df = fusion_df.fillna(method='ffill')
        for i in fusion_df.columns:
            if 'Strength' in i:
                fusion_df[i] = pd.to_numeric(fusion_df[i], downcast='float')
        del fusion_df['B']
        del fusion_df['G']
        del fusion_df['H']
        return cls(fusion_df, test_cols=[1, 3, 5])

    @classmethod
    def extrusion(cls, file_1, file_2):
        ex_df = Destruct._create_df(file_1, file_2, 2)
        ex_df.columns = ['Destruct', 'B', 'Shear Strength', 'Shear Break Code',
                         'Peel Strength', 'Peel Break Code', 'G']
        ex_df = ex_df.fillna(method='ffill')
        ex_df['Shear Strength'] = pd.to_numeric(ex_df['Shear Strength'], downcast='float')
        ex_df['Peel Strength'] = pd.to_numeric(ex_df['Peel Strength'], downcast='float')
        del ex_df['B']
        del ex_df['G']
        return cls(ex_df, test_cols=[1, 3])

    def avg_values(self, test):
        g = self._df.loc[:, f'{test} Strength'].mean()
        return f'The average {test} values are: {round(g, 2)} lbs/in.'

    def all_names(self):
        name_df = self._df
        names = name_df['Destruct'].unique()
        return str(len(names)) + ' Destructs:', names

    def get_break_c(self, test):
        df_1 = self._df
        break_count = df_1[f'{test} Break Code'].value_counts()
        return break_count

    def get_fails(self, test):
        df_1 = self._df
        df_1['Failures'] = df_1[f'{test} Break Code'].str.extract('.*\((.*)\).*', expand=True)
        fail = df_1.dropna(axis=0)
        return fail

    def plot_values(self, size=(10, 7)):
        return self._df.iloc[:, self._test_cols].plot.box(figsize=size)
