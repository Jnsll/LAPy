import os

class InputData:

    """
        Adds two numbers and returns the result.
 
        This add two real numbers and return a real result. You will want to
        use this function in any place you would usually use the ``+`` operator
        but requires a functional equivalent.
 
        :param a: The first number to add
        :param b: The second number to add
        :type a: int
        :type b: int
        :return: The result of the addition
        :rtype: int
 
        :Example:
 
        >>> add(1, 1)
        2
        >>> add(2.1, 3.4)  # all int compatible types work
        5.5
 
        .. seealso:: sub(), div(), mul()
        .. warning:: This is a completly useless function. Use it only in a 
                      tutorial unless you want to look like a fool.
        .. note:: You may want to use a lambda function instead of this.
        .. todo:: Delete this function. Then masturbate with olive oil.



    the columns of the dataframe have to be as follow:
    stress_period;	sp_length;	time_step; study (0 : TS or 1 : SS);	rech

    The first line has to be: 0.0;1.0;1.0;1.0;0.0

    Time step is 1!

    """


    def __init__(self, df_ref_data, chronicle, approximation, aggregation_rate, time_step=None):
        self.__data = df_ref_data
        self.__aggregation_rate = aggregation_rate
        self.__approximation = approximation
        self.__chronicle = chronicle

    # def set_aggregation_rate(self, aggregation_rate):
        

    # def set_approximation_type(self, approximation):
        


    # def generate_input_file(self, model_name, input_name, approx, rate, chronicle, steady, time_step=None):
    #     # TO DO : change name model_name for all case (steady, approx =1, etc)
    #     folder_path = '/'.join((os.path.dirname((os.path.abspath(__file__)))).split('/')[:-1])
    #     chronicle_file = pd.read_table(folder_path + "/data/chronicles.txt", sep=',', header=0, index_col=0)
    #     template_file = chronicle_file.template[chronicle]
    #     df = manipulate_ref_input_file(template_file,  approx, rate, steady, time_step=time_step)  => aggregate()
    #     if model_name is None:
    #         model_name = "Step1_Chronicle" + str(chronicle) + "_Approx" + str(approx) + "_Period" + str(rate)
    #     output_name = write_custom_input_file(model_name, df)
    #     return output_name


    def aggregate(self, steady_state): #, periodValue
        #df = extract_df_from_ref_input_file(template_name)
        if steady_state:
            self.__aggregate_data_for_steady_state()
        else:
            self.__aggregate_data_for_transient_state()


    def __aggregate_data_for_steady_state(self):
        # The recharge rate for the steady state is computated as the mean of the recharge rates across all the stress period of the data
        self.__aggregate_first_steady_stress_period()
        self.__data.loc[0,'rech'] = float(self.__data['rech'].mean())
        # Keep only the first stress period which is the first line of the dataframe
        self.__data = self.__data.iloc[[0]]


    def __aggregate_first_steady_stress_period(self):
        # The recharge rate for the steady state is computated as the mean of the recharge rates across all the stress period of the data
        self.__data.loc[0,'rech'] = float(self.__data['rech'].mean()) #df['rech'][0]
        print("mean init for inputfile: ", self.__data.loc[0,'rech'])

    def __aggregate_data_for_transient_state(self):
        if self.__approximation == 0:            # Use Enum for approximation!
            period = [int(self.__aggregation_rate)] #getNumberOfLinesToReduceInLoop(prd)
            indexes = self.__get_indexes_to_remain_for_a_period(len(self.__data.index), period)
        # elif self.approximation == 1:
        #         indexes = get_indexes_to_remain_for_rech_threshold(df, len(df.index), self.aggregation_rate)
        # elif self.approximation == 2:
        #     period = [int(self.aggregation_rate)]
        #     indexes = get_indexes_to_remain(len(df.index), period) #get_indexes_to_remain_approx3(len(df.index), period)
        else:
            print("The number chosen for the approximation is not valid.")
            return

        self.__aggregate_values(indexes, len(self.__data.index))
        self.__keep_only_data_with_indexes(indexes)
        
        # if time_step is not None:
        #     df = change_time_step(df, time_step)


    def __get_indexes_to_remain_for_a_period(self, number_lines, period):
        ligne = 1
        indexes = [0,1]
        period_length = len(period)
        i = 0
        while (ligne < number_lines-1):
            ligne += period[i]
            if (ligne < number_lines-1):
                indexes.append(ligne)
            if (i == (period_length-1)):
                i = 0
            else:
                i += 1
        return indexes


    def __aggregate_values(self, indexes, nb_rows):
        '''
            TODO
        '''
        
        self.__aggregate_first_steady_stress_period()
        if self.__approximation == 2:
            self. __aggregate_values_with_keeping_the_recharge_value_of_the_original_stress_period(indexes, nb_rows)
        else:
            self.__aggregate_values_with_mean_function(indexes, nb_rows)


    def __aggregate_values_with_keeping_the_recharge_value_of_the_original_stress_period(self, indexes, nb_rows):
        for i in range(1, len(indexes)):

            if i < (len(indexes)-1): # When it is not the last index of the stress periods to keep in the data
                # Update value of length of stress period 
                self.__data.iat[indexes[i], 1] = indexes[i+1] - indexes[i]
            else:                    # When it is the last index of the stress periods to keep in the data
                self.__data.iat[indexes[i], 1] = nb_rows-indexes[i]


    def __aggregate_values_with_mean_function(self, indexes, nb_rows):
        """
            .. warning:: it is to only be used with the reference data (data with the length of all the stress periods equals to 1)
        """

        for i in range(1, len(indexes)):
            #  print(indexes[3+1], indexes[3]) #Initialisation has to remain so strating at period number 1. Initialisation period is number 0.
            if i < (len(indexes)-1):
                # Compute the new value of the recharge over the period of the stress periods being aggregated
                # The function chosen here to aggregate the recharge values are the mean
                for z in range(indexes[i]+1, indexes[i+1]): #+1 pour ne pas compter la valeur df.iat[indexes[i]] une deuxième fois
                    self.__data.iat[indexes[i], 4] += self.__data['rech'][z]
                self.__data.iat[indexes[i], 4] = float(self.__data.iat[indexes[i], 4]) / (indexes[i+1] - indexes[i])
                # update of the value of the stress period length : it equals to the number of stress periods that are aggregated together
                self.__data.iat[indexes[i], 1] = indexes[i+1] - indexes[i]
            else:
                # Compute the new value of the recharge over the period of the stress periods being aggregated
                # The function chosen here to aggregate the recharge values are the mean
                for z in range(indexes[i]+1, nb_rows):
                    self.__data.iat[indexes[i], 4] += self.__data['rech'][z]
                self.__data.iat[indexes[i], 4] = self.__data.iat[indexes[i], 4] / (nb_rows - indexes[i])
                # update of the value of the stress period length : it equals to the number of stress periods that are aggregated together
                self.__data.iat[indexes[i], 1] = nb_rows-indexes[i]


    def __keep_only_data_with_indexes(self, indexes):
        indexes_to_remove = []
        # List all the indexes 
        for y in range(0, len(self.__data.index)):
            indexes_to_remove.append(y)

        # Remove the indexes to be kept in the data from the list of the indexes to be removed of the data
        for index_to_keep in indexes[:]:
            if index_to_keep in indexes_to_remove:
                indexes_to_remove.remove(index_to_keep)

        self.__data.drop(self.__data.index[indexes_to_remove], inplace=True)


    def __write_input_file(self, modelname):
        outputname = "input_file_" + modelname + ".txt"
        filepath = os.path.join('/'.join(os.path.realpath(__file__).split('/')[:-2]) , "data", outputname)
        self.__data.to_csv(filepath, sep="\t", index=False)