import os
# data science imports
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.preprocessing import StandardScaler
import json

class KnnRecommender:
    def __init__(self, file, json_str):
        """
        Recommender requires path to data: movies data and ratings data
        Parameters
        ----------
        path_movies: str, movies data file path
        path_ratings: str, ratings data file path
        """

        #json_str = '{"Name": "Suji", "business_entity": 1, "company_name": "Zoho", "experience": "2","industry_type": "2", "revenue": "20000", "zipcode": "85281","active_owners": "4", "parttime": "100", "fulltime": "20", "payroll": "4000","locations": "2"}'
        self.file = file
        self.json_str = json_str
        self.model = NearestNeighbors()

        self.baseprice = {'General liability':100,
                        'Workers compensation':110,
                        'Business Owners policy':160,
                        'Commercial Property':200,
                        'Professional Liability':180,
                        'Commercial Auto':240,
                        'Umbrella Insurance':300,
                        'Errors and omissions':120,
                        'Directors and officers':250,
                        'Employement practices and Liability Insurance':200,
                        'Inland Marine':130,
                        'Product Liability':270,
                        'Special events':150,
                        'Cyber liability':190,
                        'Liquor Liability':350,
                        'Medical malpractice':320}

        self.insurance_details =     ['General liability', 'Workers compensation',
                               'Business Owners policy', 'Commercial Property',
                               'Professional Liability', 'Commercial Auto', 'Umbrella Insurance',
                               'Errors and omissions', 'Directors and officers',
                               'Employement practices and Liability Insurance', 'Inland Marine',
                               'Product Liability', 'Special events', 'Cyber liability',
                               'Liquor Liability', 'Medical malpractice']

    def _parse_json(self):

        self.json_dict = json.loads(self.json_str)
        self.json_dict['Company name'] = self.json_dict.pop('company_name')
        self.json_dict['Address'] = self.json_dict.pop('zipcode')
        self.json_dict['# of years experience in Industry'] = self.json_dict.pop('experience')
        self.json_dict['Industry'] = self.json_dict.pop('industry_type')
        self.json_dict['Projected Annual Revenue'] = self.json_dict.pop('revenue')
        self.json_dict['Number of owners active'] = self.json_dict.pop('active_owners')
        self.json_dict['Number of employees full time'] = self.json_dict.pop('fulltime')
        self.json_dict['Number of employees parttime'] = self.json_dict.pop('parttime')
        self.json_dict['Total # of employees'] = self.json_dict['Number of employees full time'] + self.json_dict[
            'Number of employees parttime']
        self.json_dict['Type of Ownership'] = self.json_dict.pop('business_entity')
        self.json_dict['Projected Payroll for employers in next 12 months '] = self.json_dict.pop('payroll')
        self.json_dict['Number of locations'] = self.json_dict.pop('locations')



        #preparing the data
        return self._prep_data(self.json_dict)

    def _inference(self, df, df_features, user):
        nbrs = NearestNeighbors(n_neighbors=2, algorithm='ball_tree').fit(df_features)
        distances, indices = nbrs.kneighbors(df_features)
        return self.make_recommendations(df, user, indices)

    def make_recommendations(self, df, query, indices):
        #getting the index according to the company name
        def get_index_from_name(name):
            return df[df["Company name"] == name].index.tolist()[0]

        #getting nearest neighbors
        if query:
            risk_profile = dict()
            found_id = get_index_from_name(query)
            for id in indices[found_id][1:]:
                x = df.loc[id][self.insurance_details]
                x = x.to_dict()
                risk_profile[id] = x
            policy_price = {}
            policy_price1={}
            for k, v in risk_profile.items():
                for k1 in v.keys():
                    policy_price[str(k)] = {}
                    policy_price1[k1] = {}
                    policy_price1[k1]['price'] = v[k1] * self.baseprice[k1]
                    policy_price1[k1]['risk'] = v[k1]
                    policy_price[str(k)]=policy_price1
            policy_price_final=json.dumps(policy_price)
            print("Final json:",policy_price_final)
            return policy_price_final
        return {}



    def _prep_data(self, json):
        # read the file
        cmp = pd.read_csv(self.file)

        #save the user information
        user = json['Company name']

        #merging input user details
        df_json = pd.DataFrame(json, index=[0])
        df_json.drop(['Name'], axis=1, inplace=True)
        cmp_final = pd.concat([cmp, df_json], axis=0, sort=True).reset_index()
        cmp_final.fillna(0, inplace=True)

        #drop out the policy details
        cmp2 = cmp_final.drop(self.insurance_details, axis = 1)

        #drop out variables not needed for model fitting
        cmp2 = cmp2.drop(["Company name", "Total # of employees", "Business Start year"], axis=1)

        #feature extraction of address
        cmp2['Address_group'] = cmp2['Address'].astype(str).str[:2]
        cmp2.drop('Address', axis=1, inplace=True)

        binscategorical =   ['Number of employees full time', 'Number of employees parttime',
                            '# of years experience in Industry', 'Projected Annual Revenue',
                            'Projected Payroll for employers in next 12 months ']

        #binning continuous variables
        kbd = KBinsDiscretizer(n_bins=10, encode='ordinal',
                               strategy='quantile')  # read documentation for encode and strategy
        dfkbd = pd.DataFrame(kbd.fit_transform(cmp2[binscategorical]), columns=['kbd_' + x for x in binscategorical])
        cmp_bins = pd.concat([cmp2, dfkbd], axis=1)
        cmp_bins = cmp_bins.drop(binscategorical, axis=1)

        #feature engineering for categorical variables- get_dummies
        categorical_new = ['Industry', 'Type of Ownership', 'Address_group', 'kbd_Number of employees full time',
                           'kbd_Number of employees parttime',
                           'kbd_# of years experience in Industry', 'kbd_Projected Annual Revenue',
                           'kbd_Projected Payroll for employers in next 12 months ']
        cmp_bins[categorical_new] = cmp_bins[categorical_new].astype(str)
        cmp_catdumm = pd.get_dummies(cmp_bins[categorical_new], drop_first=True)  # dummy_na=True
        cmp_catdumm = pd.concat([cmp_bins, cmp_catdumm], axis=1)
        cmp_catdumm = cmp_catdumm.drop(categorical_new, axis=1)

        #Scaling numerical variables
        numericvars = ['Number of owners active ', 'Number of locations']
        ss = StandardScaler(with_mean=True, with_std=True)
        cmp_catdummss = pd.DataFrame(ss.fit_transform(cmp_catdumm[numericvars]),
                                     columns=['ss_' + x for x in numericvars])
        cmp_catdummss = pd.concat([cmp_catdumm, cmp_catdummss], axis=1)
        cmp_catdummss = cmp_catdummss.drop(numericvars, axis=1)

        return self._inference(cmp_final, cmp_catdummss, user)

if __name__ == '__main__':
    knn = KnnRecommender("C://Users//Ganesh Kumar//Downloads//Companies_Insurances.csv")
    knn._parse_json()
