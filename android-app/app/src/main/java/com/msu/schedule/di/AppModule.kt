package com.msu.schedule.di

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import com.msu.schedule.data.remote.ScheduleParser
import com.msu.schedule.data.repository.ScheduleRepository
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    
    @Provides
    @Singleton
    fun provideScheduleParser(): ScheduleParser {
        return ScheduleParser()
    }
    
    @Provides
    @Singleton
    fun provideScheduleRepository(parser: ScheduleParser): ScheduleRepository {
        return ScheduleRepository(parser)
    }
}
