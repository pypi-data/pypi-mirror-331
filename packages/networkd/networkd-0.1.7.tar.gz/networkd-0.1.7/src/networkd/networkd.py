import pandas as pd
import numpy as np

class Embed: 

    @staticmethod
    def prep_data(data, labels = False):
        '''
        Intake a pandas dataframe or dictionary of two series or lists of type categorical which 
        describe the occurence of categories(1st) inside the entities (2nd) of a bi-parite graph. 
        A 3rd numerical list which describes the degree of the relationship of the category within 
        the entity is optional. If not inlcuded a list of 1's will be assigned. 
        
        Parameters
        ----------
        data: pandas dataframe or dicionary of two series or lists of type categorical

        Returns
        -------
        np_adj: a numpy array of the dimensions [number of unique cateogries, number of unique entities]
        '''

        if isinstance(data, dict):
            if all(isinstance(col, list) for col in data.values()):
                pass
            else: 
                value_types = [type(x) for x in data.values()]
                raise ValueError(f'Dictionary values must be lists. Got types {value_types} instead')

        elif isinstance(data, pd.DataFrame):
                data = data.to_dict(orient='list')
            
        else:
            raise TypeError(f'data must be a pandas dataframe or dictionary. Got type {type(data)} instead')

        if len(data) < 3:
            data['value'] = np.ones(len(next(iter(data.values()))), dtype=int).tolist()
        
        
        keys = list(data.keys())

        row_labels, col_labels = (np.unique(data[k]) for k in list(data.keys())[:2])

        row_map = {label: i for i, label in enumerate(row_labels)}
        col_map = {label: i for i, label in enumerate(col_labels)}

        np_adj = np.zeros((len(row_labels), len(col_labels)), dtype = int)

        for r, c, v in zip(data[keys[0]], data[keys[1]], data[keys[2]]):
            np_adj[row_map[r], col_map[c]] = v

        if labels: 

            return np_adj, row_labels, col_labels
        
        else: 

            return np_adj

        
    @staticmethod
    def filter_df(np_adj, threshold):
        '''
        Intake a numpy array adjacency matrix and filter the values by 
        if the share of the category value within an entity is greater than 
        the share of the entire cateogry (data[0]) across all entities (data[1]). 
        
        Parameters
        ----------
        data: pandas dataframe 

        Returns
        -------
        filtered_data: adjacency matrix as an n(# of categories) by m(# of entities) numpy array. 
        '''
        if isinstance(np_adj, np.ndarray): 
            pass
        else:
            raise TypeError(f'input must be a numpy array, got {type(np_adj)} instead')
        
        cat_share_in_ent = np_adj / np_adj.sum(axis = 0, keepdims = True)
        cat_share_all = np_adj.sum(axis = 1, keepdims = True) / np_adj.sum()

        rca_np = cat_share_in_ent / cat_share_all

        rca_np = np.where(rca_np < threshold, 0, 1)

        return rca_np 
        
                
    @staticmethod
    def co_occurence(rca_np, self_loops):
        '''
        Intake an rca filtered pandas dataframe and calculate a co-occurence matrix by 
        computing the conditional probability that given the most frequent category another 
        category will also appear in the same entity for all pairings of categories. 

        Parameters
        ----------
        data: pandas dataframe 

        Returns
        -------
        df: pandas dataframe
        
        '''
        #print(f'rca in co-occurence function {rca_np}')
        gram_np = np.dot(rca_np, rca_np.T)

        degree = np.count_nonzero(rca_np, axis = 1)

        gram_np = gram_np / degree 

        network = np.minimum(gram_np, gram_np.T)

        if self_loops:
            pass
        else:
            np.fill_diagonal(network, 0)

        return network

                
    @staticmethod            
    def embed(data, rca = True, threshold = 1, self_loops = True):
        '''
        Call helper functions prep_data and filter_df if necessary in order to embed the data
        by constructing a co-occurence matrix of the bi-partite graph.  
        
        Parameters
        ----------
        data: pandas dataframe 

        Returns
        -------
        co_occ_df: numpy array of the co-occurence matrix. 
        '''
        matrix = Embed.prep_data(data)
        if rca:
            matrix = Embed.filter_df(matrix, threshold)
        co_occ_np = Embed.co_occurence(matrix, self_loops)
        return co_occ_np




            


