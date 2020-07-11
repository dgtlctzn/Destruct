import pandas as pd


class Destruct:

    def __init__(self, df, test_nums=None):
        self._df = df
        self._test_nums = test_nums

    def __str__(self):
        return f'{self._df}'

    # dataframe construction common to both extrusion and fusion tests
    @staticmethod
    def _create_df(file, col):
        combo_df = pd.concat(pd.read_excel(file, sheet_name=None, header=None))
        combo_df = combo_df.dropna(thresh=4, axis=0)
        filter_1 = combo_df.iloc[:, col] != 'STRENGTH'
        filter_2 = combo_df.iloc[:, col] != '(ppi)'
        filter_3 = combo_df.iloc[:, col] != '-'
        combo_df = combo_df[filter_1 & filter_2 & filter_3]
        return combo_df

    @classmethod
    def fusion(cls, file):
        fusion_df = Destruct._create_df(file, 1)
        fusion_df.columns = ['Destruct', 'Shear Strength', 'Shear Break Code', 'D', 'Top Peel Strength',
                             'Top Peel Break Code', 'G', 'Bottom Peel Strength', 'Bottom Peel Break Code', 'J']
        fusion_df = fusion_df.fillna(method='ffill')
        for i in fusion_df.columns:
            if 'Strength' in i:
                fusion_df[i] = pd.to_numeric(fusion_df[i], downcast='float')
        fusion_df = fusion_df.drop(['D', 'G', 'J'], axis=1)
        return cls(fusion_df, test_nums=[1, 3, 5])

    @classmethod
    def extrusion(cls, file):
        ex_df = Destruct._create_df(file, 2)
        ex_df.columns = ['Destruct', 'B', 'Shear Strength', 'Shear Break Code', 'Peel Strength',
                         'Peel Break Code', 'G']
        ex_df = ex_df.fillna(method='ffill')
        ex_df['Shear Strength'] = pd.to_numeric(ex_df['Shear Strength'], downcast='float')
        ex_df['Peel Strength'] = pd.to_numeric(ex_df['Peel Strength'], downcast='float')
        ex_df = ex_df.drop(['B', 'G'], axis=1)
        return cls(ex_df, test_nums=[1, 3])

    # gives average strengths for all tests of a particular type ie. peel/shear
    def avg_values(self, test):
        g = self._df.loc[:, f'{test} Strength'].mean()
        return f'The average {test} values are: {round(g, 2)} lbs/in.'

    # returns the id of each destruct
    def all_names(self):
        name_df = self._df
        names = name_df['Destruct'].unique()
        return str(len(names)) + ' Destructs:', names

    # each destruct is assigned a type based on the way it reacts to being pulled apart
    def get_break_c(self, test):
        df_1 = self._df
        break_count = df_1[f'{test} Break Code'].value_counts()
        return break_count

    # Fails are destructs with improperly welded seams
    def get_fails(self, test):
        df_1 = self._df
        test_s = f'{test} Strength'
        test = f'{test} Break Code'
        fail_slice = df_1.loc[df_1[test].str.contains('AD'), ['Destruct', test_s, test]]
        if not fail_slice.empty:
            return fail_slice
        else:
            raise ValueError('No failures found in data-set')

    # gives a quick visualization of the median/range of the strengths of all test types
    def plot_values(self, size=(10, 7)):
        return self._df.iloc[:, self._test_nums].plot.box(figsize=size)
